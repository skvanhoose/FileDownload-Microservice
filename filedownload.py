from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas
import io
import csv


# accept only JSON strings with this structure
class myReq(BaseModel):
    title: str
    filetype: str
    data: list


app = FastAPI()

# to test locally, add your port to origins list. Ex: http://localhost:<PORT>
origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.post('/file-download')
async def stream_file(req: myReq):
    try:
        file_name = req.title.lower()
        if req.filetype == 'csv':
            media_type = 'text/csv'
            file_name += '.csv'
            headers = req.data[0].keys()
            # write to string buffer
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(req.data)
            output.seek(0)

        elif req.filetype == 'excel':
            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_name += '.xlsx'
            output = io.BytesIO()
            writer = pandas.ExcelWriter(output, engine='xlsxwriter')
            df = pandas.DataFrame(req.data)
            df.to_excel(writer, index=False)
            writer.close()
            output.seek(0)

        else:
            raise HTTPException(status_code=406, detail='Filetype is unsupported for download')

    except:
        raise HTTPException(status_code=400, detail='Payload must include title, filetype, and data')

    return StreamingResponse(
        output,
        media_type=media_type,
        # Add your port to localhost for local testing
        headers={'Content-Disposition': f'attachment; filename="{file_name}"',
                 'Access-Control-Expose-Headers': 'Content-Disposition'}
    )
