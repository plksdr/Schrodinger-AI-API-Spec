from flask import Flask, request
from flask_restful import Api, Resource, reqparse, inputs, abort
from marshmallow import Schema, fields, validate, ValidationError
import uuid
import base64
import os
_curdir = os.path.dirname(__file__)

app = Flask(__name__)
api = Api(app)
with open(os.path.join(_curdir, 'sample.webp'), 'rb') as fi:
    _mock_image = base64.b64encode(fi.read()).decode('utf8')
with open(os.path.join(_curdir, 'sample-watermarked.webp'), 'rb') as fi:
    _mock_image_wm = base64.b64encode(fi.read()).decode('utf8')

# Schemas for request validation using Marshmallow
class AttributeSchema(Schema):
    traitType = fields.Str(required=True)
    value = fields.Str(required=True)

class ImageGenerationRequestSchema(Schema):
    seed = fields.Str(required=True, validate=validate.Regexp("^[1-9]\\d{0,31}$"))
    newAttributes = fields.List(fields.Nested(AttributeSchema), required=True)
    numImages = fields.Int(required=True, validate=validate.Range(min=1, max=10))

class ImageQueryRequestSchema(Schema):
    requestId = fields.Str(required=True)

class ImageProcessRequestSchema(Schema):
    sourceImage = fields.Str(required=True)
    watermark = fields.Str(required=True)

# Helper function to validate request data
def validate_request(schema, data):
    try:
        schema().load(data)
    except ValidationError as err:
        abort(400, message=str(err.messages))

class ImageGenerate(Resource):
    def post(self):
        validate_request(ImageGenerationRequestSchema, request.json)
        return {'requestId': str(uuid.uuid4())}, 200

class ImageQuery(Resource):
    def post(self):
        validate_request(ImageQueryRequestSchema, request.json)
        return {'images': [
            {'image': f'data:image/webp;base64,{_mock_image}', 'attributes': [{'traitType': 'Hat', 'value': 'fedora hat'}]},
            {'image': f'data:image/webp;base64,{_mock_image}', 'attributes': [{'traitType': 'Hat', 'value': 'fedora hat'}]}
            ]}, 200

class ImageProcess(Resource):
    def post(self):
        validate_request(ImageProcessRequestSchema, request.json)
        return {'processedImage': f'data:image/webp;base64,{_mock_image_wm}'}, 200

# Adding resources to API
api.add_resource(ImageGenerate, '/image/generate')
api.add_resource(ImageQuery, '/image/query')
api.add_resource(ImageProcess, '/image/process')

if __name__ == '__main__':
    app.run(debug=True, port=9010)
