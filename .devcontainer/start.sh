sudo apt-get update && sudo apt-get install ffmpeg libsm6 libxext6 -y

conda create -n HivisionIDPhotos python=3.10 -y
conda init
echo 'conda activate HivisionIDPhotos' >> ~/.bashrc

ENV_PATH="/opt/conda/envs/HivisionIDPhotos/bin"
$ENV_PATH/pip install -r requirements.txt -r requirements-app.txt -r requirements-dev.txt

$ENV_PATH/python scripts/download_model.py --models all
