import logging
import torch
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint
from classifier import LitClassifier, ClassifierV2, Classifier
from dataset.extracted_dataset import KeypointExtractedDatasetV2
from detectron_utils import *
from constant import *

logging.basicConfig(level=logging.INFO)

setup_dataset('semaphore_keypoint_train', 'data/train/annotation.json', 'data/train')
setup_dataset('semaphore_keypoint_val', 'data/val/annotation.json', 'data/val')

train_dataset = KeypointExtractedDatasetV2('semaphore_keypoint_train', 'data/train/df2.csv')
val_dataset = KeypointExtractedDatasetV2('semaphore_keypoint_val', 'data/val/df2.csv')
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS)
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
classifier = LitClassifier(6 * 2, 28, ClassifierV2)

logger = TensorBoardLogger(save_dir=os.getcwd(), name='runs', version='improved')
early_stop_cb = EarlyStopping(monitor='validation/acc', patience=100, verbose=True, mode='max')
checkpoint_cb = ModelCheckpoint(monitor='validation/acc', save_top_k=1, mode='max')
trainer = pl.Trainer(
    logger=logger,
    max_epochs=MAX_EPOCHS,
    check_val_every_n_epoch=1,
    default_root_dir=os.getcwd(),
    log_every_n_steps=1,
    accelerator='gpu',
    devices=1,
    callbacks=[early_stop_cb, checkpoint_cb],
)
trainer.fit(classifier, train_loader, val_loader)