from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas
import io
import csv


class myReq(BaseModel):
    title: str
    filetype: str
    data: list


app = FastAPI()

origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

def create_csv(data):
    if not data:
        raise HTTPException(status_code=400, detail="Data cannot be empty")

    headers = data[0].keys()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)

    return output


def create_excel(data):
    output = io.BytesIO()

    writer = pandas.ExcelWriter(output, engine='xlsxwriter')
    df = pandas.DataFrame(data)

    df.to_excel(writer, index=False)
    writer.close()

    output.seek(0)

    return output

@app.post('/file-download')
async def stream_file(req: myReq):

    file_name = req.title.lower()

    if req.filetype == "csv":
        output = create_csv(req.data)
        media_type = "text/csv"
        file_name += ".csv"

    elif req.filetype == "excel":
        output = create_excel(req.data)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        file_name += ".xlsx"

    else:
        raise HTTPException(status_code=406, detail="Unsupported filetype")

    return StreamingResponse(
        output,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )