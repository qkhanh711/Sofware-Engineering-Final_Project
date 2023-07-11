from typing import Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from Generate import generate
from utils import convert2_

app = FastAPI()

class MyImage(BaseModel):
    image: str

class Caption(BaseModel):
    cap : str


@app.post("/generateImage")
def gen(models: str, path: str = None, prompt: str = None):
    model,result = generate(convert2_(models),number=1, idx = 1
                            , prompt = prompt,url = convert2_(path))
    
    images = MyImage(
        image=str(result)
    )

    caption = Caption(
        cap = str(result)
    )

    if model == "nlpconnect/vit-gpt2-image-captioning":
        return {"generated_texts": jsonable_encoder(caption)}
    else:
        return {"generated_images": jsonable_encoder(images)}

@app.get("/uploadImage")
def uploadImage(upload_image: MyImage):
    print(upload_image.image)
    return {"uploadImage": jsonable_encoder(upload_image)}


