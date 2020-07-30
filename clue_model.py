"""
Clue model

Neural network based on fine-tuned BERT model

input: crossword clue text
output: (TBA - LISTING IDEAS)
 -> most likely answer(s)?
 -> probability of a given answer (would be included in input?)

TODO: read more about BERT/other language model tasks and see which is best fit
"""


from absl import app, flags, logging

import torch as th
import pytorch_lightning as pl

import nlp
import transformers

flags.DEFINE_boolean('debug', True, '')
flags.DEFINE_integer('batch_size', 8, '')
flags.DEFINE_integer('epochs', 10, '')
flags.DEFINE_float('lr', 1e-2, '')
flags.DEFINE_float('momentum', 0.9, '')
flags.DEFINE_string('model', 'bert-base-uncased', '')
flags.DEFINE_integer('seq_length', 32, '')
FLAGS = flags.FLAGS


class CrosswordSolver(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = transformers.BertForSequenceClassification(FLAGS.model)

    def prepare_data(self):
        tokenizer = transformers.BertTokenizerFast.from_pretrained(FLAGS.model)
        def _tokenize(x):
            x['input_ids'] = tokenizer.encode(
                x['text'],
                max_length=FLAGS.seq_length,
                pad_to_max_length=True)
            return x

        def _prepare_ds(split):
            ds = nlp.load_dataset('imdb', split=f'{split}[:{FLAGS.batch_size}]' if FLAGS.debug else f'{split}[:5%]')
            ds = ds.map(_tokenize)
            ds.set_format(type='torch', output_all_columns=['input_ids', 'label'])
            return ds

        self.train_ds, self.test_ds = map(_prepare_ds, ('train', 'test'))

    def forward(self, batch):
        import IPython; IPython.embed(); exit(1)

    def training_step(self, batch, batch_idx):
        import IPython; IPython.embed(); exit(1)

    def train_dataloader(self):
        return th.utils.data.DataLoader(
            self.train_ds,
            batch_size = FLAGS.batch_size,
            drop_last=True,
            shuffle=True
        )

    def val_dataloader(self):
        return th.utils.data.DataLoader(
            self.test_ds,
            batch_size = FLAGS.batch_size,
            drop_last=False,
            shuffle=False
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
        default_root_dir='logs',
        gpus=(1 if th.cuda.is_available() else 0),
        max_epochs=FLAGS.epochs,
    )
    trainer.fit(model)


if __name__ == '__main__':
    app.run(main)