from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
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
async def download_csv(req: myReq):
    file_name = req.title
    if req.filetype == 'CSV':
        file_name += '.csv'
        headers = req.data[0].keys()
        # write to string buffer
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(req.data)
        output.seek(0)

    elif req.filetype == 'Excel':
        my_message = {'message': 'This logic needs to be implemented'}
        return my_message

    else:
        raise HTTPException(status_code=406, detail='Filetype is unsupported for download')

    return StreamingResponse(
        output,
        media_type='text/csv',
        # Add your port to localhost for local testing
        headers={'Content-Disposition': f'attachment; filename="{file_name}"',
                 'Access-Control-Expose-Headers': 'Content-Disposition'}
    )
