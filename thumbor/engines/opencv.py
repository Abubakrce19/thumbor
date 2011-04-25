#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tempfile

from tornado.options import options
import cv

from thumbor.engines import BaseEngine

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}

class Engine(BaseEngine):

    def create_image(self, buffer):
        imagefiledata = cv.CreateMatHeader(1, len(buffer), cv.CV_8UC1)
        cv.SetData(imagefiledata, buffer, len(buffer))
        img0 = cv.DecodeImage(imagefiledata, cv.CV_LOAD_IMAGE_COLOR)

        return img0

    @property
    def size(self):
        return cv.GetSize(self.image)

    def normalize(self):
        pass

    def resize(self, width, height):
        thumbnail = cv.CreateMat(int(round(height, 0)), int(round(width, 0)), cv.CV_8UC3)
        cv.Resize(self.image, thumbnail)
        self.image = thumbnail

    def crop(self, left, top, right, bottom):
        new_width = right - left
        new_height = bottom - top
        cropped = cv.CreateImage((new_width, new_height), 8, 3)
        src_region = cv.GetSubRect(self.image, (left, top, new_width, new_height) )
        cv.Copy(src_region, cropped)

        self.image = cropped

    def flip_vertically(self):
        raise NotImplementedError()

    def flip_horizontally(self):
        raise NotImplementedError()

    def read(self, extension=None, quality=options.QUALITY):
        with tempfile.NamedTemporaryFile(suffix=self.extension) as temp_file:
            img = self.image
            if FORMATS[self.extension] == 'JPEG':
                img = cv.DecodeImage(cv.EncodeImage(".jpeg", img, [cv.CV_IMWRITE_JPEG_QUALITY, quality]))
            cv.SaveImage(temp_file.name, img)
            temp_file.seek(0)
            return temp_file.read()
