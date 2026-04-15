import tensorflow as tf
import os

# ================== PATH FIX ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")

DATASET_PATH = os.path.join(PROJECT_DIR, "dataset")
MODEL_DIR = os.path.join(PROJECT_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "disease_model.h5")

# Ensure models folder exists
os.makedirs(MODEL_DIR, exist_ok=True)

print("Dataset Path:", DATASET_PATH)
print("Model Save Path:", MODEL_PATH)

# ================== DATA ==================
train = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_data = train.flow_from_directory(
    DATASET_PATH,
    target_size=(128,128),
    batch_size=32,
    class_mode='binary',
    subset='training'
)

val_data = train.flow_from_directory(
    DATASET_PATH,
    target_size=(128,128),
    batch_size=32,
    class_mode='binary',
    subset='validation'
)

print("Class Indices:", train_data.class_indices)

# ================== MODEL ==================
model = tf.keras.models.Sequential([
    tf.keras.Input(shape=(128,128,3)),   # 🔥 FIX (warning removed)

    tf.keras.layers.Conv2D(32,(3,3),activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),

    tf.keras.layers.Conv2D(64,(3,3),activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128,activation='relu'),
    tf.keras.layers.Dropout(0.5),

    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# ================== TRAIN ==================
print("\n🔥 Training Started...\n")

history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=15
)

print("\n✅ Training Finished")

# ================== SAVE ==================
model.save(MODEL_PATH)

print(f"\n✅ Model Saved Successfully at:\n{MODEL_PATH}")