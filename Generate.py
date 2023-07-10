import torch.optim as optim
from Generative_models.ProgressiveGAN import config as config_progressive
from Generative_models.ProgressiveGAN.utils import *
from Generative_models.ProgressiveGAN.model import *
from Generative_models.ProgressiveGAN.train import *

from Generative_models.simpleVAE import config as config_VAE
from Generative_models.simpleVAE.utils import *
from Generative_models.simpleVAE.VAE import *

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

import PIL
import requests
from PIL import Image

from utils import predict_step
import subprocess

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def download_image(url):
    image = PIL.Image.open(requests.get(url, stream=True).raw)
    image = PIL.ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    return image

def generate_with_scratch_model(model_name, path, number = 1):
    if model_name == "ProGAN":
        gen = Generator(config_progressive.Z_DIM, config_progressive.IN_CHANNELS, img_channels=config_progressive.CHANNELS_IMG).to(config_progressive.DEVICE)
        opt_gen = optim.Adam(gen.parameters(), lr=config_progressive.LEARNING_RATE, betas=(0.0, 0.99))

        load_checkpoint('/home/nyanmaruk/Uni/weightCelebA/generator.pth', gen, opt_gen, config_progressive.LEARNING_RATE)
        generate_examples(gen, 3, root_path= path, n = number)
    else:
        dataset = datasets.MNIST(root="../datasets/mnist", train=True, transform=transforms.ToTensor(), download = True)
        model = VAE(config_VAE.in_dims, config_VAE.h_dims, config_VAE.z_dims).to(config_VAE.device)
        optimizer = optim.Adam(model.parameters(), lr=config_VAE.lr)
        
        load_checkpoint('/home/nyanmaruk/Uni/weightVAE/VAE.pth', model, optimizer, config_VAE.lr)
        for idx in range(10):
            inference(dataset, model, idx, num_examples=number)
    print(f"Results saved to {path}/{model_name}")

def generate_with_pretrained_model(name, prompt, url = None):
    """
       url: URL links or path of image

       Name models : 'hakurei/waifu-diffusion'
       promt       :"1kid, aqua eyes, baseball cap, red hair, closed mouth, earrings, green background 
       , hat, hoop earrings, jewelry, looking at viewer, shirt, short hair, simple background, solo, upper body, blue shirt" 
    
       Name models : "runwayml/stable-diffusion-v1-5"
       promt       : "a photo of an astronaut riding a horse on mars"

       Name models : "timbrooks/instruct-pix2pix"
       promt       : "turn him into cyborg"
       """
    if name == "nlpconnect/vit-gpt2-image-captioning":
        return predict_step(url)
    elif name == "GFPGAN":
        command = [
            "python",
            "/home/nyanmaruk/Uni/Sofware-Engineering-Final_Project/pretrained/GFPGAN/inference_gfpgan.py",
            "-i",
            "pretrained/GFPGAN/inputs/upload",
            "-o",
            "pretrained/GFPGAN/results",
            "-v",
            "1.3",
            "-s",
            "2",
            "--bg_upsampler",
            "realesrgan"
        ]
        subprocess.run(["rm", "-rf", "pretrained/GFPGAN/results"], cwd="/home/nyanmaruk/Uni/Sofware-Engineering-Final_Project")
        subprocess.run(command, cwd="/home/nyanmaruk/Uni/Sofware-Engineering-Final_Project")
        subprocess.run(["ls", "pretrained/GFPGAN/results/cmp"], cwd="/home/nyanmaruk/Uni/Sofware-Engineering-Final_Project")
    else:
        pipe = StableDiffusionPipeline.from_pretrained(
        name,
        torch_dtype=torch.float32,
        safety_checker=None
        ).to(device)
        with autocast("cpu"):
            if name == 'hakurei/waifu-diffusion':
                image = pipe(prompt, guidance_scale=6)["images"][0]
            elif name == "runwayml/stable-diffusion-v1-5":
                image = pipe(prompt).images[0] 
            elif name == "timbrooks/instruct-pix2pix":
                pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
                img = download_image(url)
                image = pipe(prompt, image=img, num_inference_steps=10, image_guidance_scale=1).images[0]
            return image


if __name__ == '__main__':
    # generate_with_scratch_model("VAE", path = '/home/nyanmaruk/Uni/Sofware-Engineering-Final_Project/Generate_images')

    url = "https://raw.githubusercontent.com/timothybrooks/instruct-pix2pix/main/imgs/example.jpg"
    prompt = "turn him into cyborg"
    url = ["/home/nyanmaruk/Uni/Sofware-Engineering-Final_Project/pretrained/GFPGAN/inputs/upload/deptry.jpg"]
    
    print(generate_with_pretrained_model('GFPGAN', prompt=prompt, url = url))
