import keras_cv
import tensorflow as tf
from tensorflow import keras
import tensorflow_datasets as tfds
import time

print(tf.__version__)
print(keras_cv.__version__)

# Create a preprocessing pipeline
augmenter = keras_cv.layers.Augmenter(
    layers=[
        keras_cv.layers.RandomFlip(),
        keras_cv.layers.RandAugment(value_range=(0, 255)),
        keras_cv.layers.CutMix(),
        keras_cv.layers.MixUp()
    ]
)

def preprocess_data(images, labels, augment=False):
    labels = tf.one_hot(labels, 3)
    inputs = {"images": images, "labels": labels}
    outputs = augmenter(inputs) if augment else inputs
    return outputs['images'], outputs['labels']

# Augment a `tf.data.Dataset`
train_dataset, test_dataset = tfds.load(
    'rock_paper_scissors',
    as_supervised=True,
    split=['train', 'test'],
)
train_dataset = train_dataset.batch(16).map(
    lambda x, y: preprocess_data(x, y, augment=True),
        num_parallel_calls=tf.data.AUTOTUNE).prefetch(
            tf.data.AUTOTUNE)
test_dataset = test_dataset.batch(16).map(
    preprocess_data, num_parallel_calls=tf.data.AUTOTUNE).prefetch(
        tf.data.AUTOTUNE)

cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath="checkpoint/weights.{epoch:02d}-{accuracy:.3f}-{loss:.3f}-{val_accuracy:.3f}-{val_loss:.3f}.h5",
                                                    save_weights_only=False,
                                                    verbose=1,
                                                    monitor='accuracy',
                                                    save_freq='epoch')
# Create a model
darknet21 = keras_cv.models.DarkNet21(
    include_rescaling=True,
    include_top=True,
    classes=3
)
darknet21.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

print(darknet21.summary())
# Train your model
start_time = time.time()
darknet21.fit(train_dataset, validation_data=test_dataset, epochs=5)
end_time = time.time()
print('Elapsed Time: %0.4f seconds' % (end_time - start_time))
print('Elapsed Time: %0.4f minutes' % ((end_time - start_time)/60))