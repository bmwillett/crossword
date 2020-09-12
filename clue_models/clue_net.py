"""
Neural network based crossword solver using BERT
"""

# TODO:
#  - issue with loss
#  - better way to set up model?
#  - train on GPU

from absl import app, flags, logging

import torch as th
import pytorch_lightning as pl
from nlp.arrow_dataset import Dataset

import nlp
import transformers

import pandas as pd

flags.DEFINE_boolean('debug', False, '')
flags.DEFINE_integer('epochs', 1, '')
flags.DEFINE_integer('batch_size', 8, '')
flags.DEFINE_float('lr', 1e-2, '')
flags.DEFINE_float('momentum', .9, '')
flags.DEFINE_string('model', 'bert-base-uncased', '')
flags.DEFINE_integer('seq_length', 32, '')

FLAGS = flags.FLAGS


class CrosswordSolver(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = transformers.BertForMaskedLM.from_pretrained(FLAGS.model)
        self.loss = th.nn.NLLLoss(reduction='none')

    def prepare_data(self):
        tokenizer = transformers.BertTokenizer.from_pretrained(FLAGS.model)

        def _tokenize(x):
            x['tokens'] = tokenizer.batch_encode_plus(
                    x['merged'],
                    max_length=FLAGS.seq_length,
                    pad_to_max_length=True)['input_ids']
            x['answer_tokens'] = [t[1] for t in tokenizer.batch_encode_plus(
                x['answer'],
                max_length=3)['input_ids']]
            return x

        # don't know how to force reload here: need to delete './temp/csv' to force reload
        ds = nlp.load_dataset('csv',
                              data_files={'train': './data/clues_train.csv',
                                          'test': './data/clues_test.csv'},
                              cache_dir='../temp')
        self.train_ds = ds['train'].map(_tokenize, batched=True)
        self.train_ds.set_format(type='torch', columns=['tokens', 'answer_tokens'], output_all_columns=False)
        self.test_ds = ds['test'].map(_tokenize, batched=True)
        self.test_ds.set_format(type='torch', columns=['tokens', 'answer_tokens'], output_all_columns=False)

    def forward(self, input_ids):
        mask = (input_ids != 0).float()
        logits, = self.model(input_ids, mask)
        return logits[:, 1, :]

    def training_step(self, batch, batch_idx):
        logits = self.forward(batch['tokens'])
        loss = self.loss(logits, batch['answer_tokens']).mean()
        return {'loss': loss, 'log': {'train_loss': loss}}

    def validation_step(self, batch, batch_idx):
        logits = self.forward(batch['tokens'])
        loss = self.loss(logits, batch['answer_tokens'])
        acc = (logits.argmax(-1) == batch['answer_tokens']).float()
        return {'loss': loss, 'acc': acc}

    def validation_epoch_end(self, outputs):
        loss = th.cat([o['loss'] for o in outputs], 0).mean()
        acc = th.cat([o['acc'] for o in outputs], 0).mean()
        out = {'val_loss': loss, 'val_acc': acc}
        return {**out, 'log': out}

    def train_dataloader(self):
        return th.utils.data.DataLoader(
                self.train_ds,
                batch_size=FLAGS.batch_size,
                drop_last=True,
                shuffle=True,
                )

    def val_dataloader(self):
        return th.utils.data.DataLoader(
                self.test_ds,
                batch_size=FLAGS.batch_size,
                drop_last=False,
                shuffle=True,
                )

    def configure_optimizers(self):
        return th.optim.SGD(
            self.parameters(),
            lr=FLAGS.lr,
            momentum=FLAGS.momentum,
        )


def main(_):
    model = CrosswordSolver()
    trainer = pl.Trainer(
        default_root_dir='../logs',
        gpus=(1 if th.cuda.is_available() else 0),
        max_epochs=FLAGS.epochs,
        fast_dev_run=FLAGS.debug,
        #logger=pl.loggers.TensorBoardLogger('logs/', name='imdb', version=0),
    )
    trainer.fit(model)
    import IPython; IPython.embed(); exit(1)


if __name__ == '__main__':
    app.run(main)