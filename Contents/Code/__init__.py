# Copyright 2013-2016 Dominik Cebula

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import json
import urllib
import urllib2

TITLE = 'GoldVODtv'
PREFIX = '/video/goldvodtv'


def Start():
    return None


@handler(PREFIX, TITLE)
def MainMenu():
    oc = ObjectContainer()

    username = Prefs['login']
    password = Prefs['password']

    if credentialsAreInvalid(username, password):
        displayCredentialsInvalidMessage(oc)
    else:
        channels = getChannels(username, password)
        if len(channels) > 0:
            displayChannels(oc, channels)
        else:
            displayChannelsNotFetchedWarningMessage(oc)

    return oc


def getChannels(username, password):
    webServiceUrl = 'http://goldvod.tv/api/get_tv_channels'
    requestHeader = {'User-Agent': 'PLEX', 'ContentType': 'application/x-www-form-urlencoded'}
    requestPost = {'login': username, 'pass': password}
    encodedData = urllib.urlencode(requestPost)
    reqUrl = urllib2.Request(webServiceUrl, encodedData, requestHeader)
    responseJson = urllib2.urlopen(reqUrl)
    return json.load(responseJson)


def displayChannels(oc, channels):
    for channel in channels:
        oc.add(
            createVideoClipObject(
                title=channel['name'],
                url=getChannelUrl(channel),
                thumb=channel['icon']
            )
        )


def getChannelUrl(channel):
    if Prefs['use_hd'] and channel['url_hd']:
        return channel['url_hd']
    else:
        return channel['url_sd']


@route(PREFIX + '/createvideoclipobject')
def createVideoClipObject(title, url, thumb, container=False):
    videoClipObject = VideoClipObject(
        key=Callback(createVideoClipObject, title=title, url=url, thumb=thumb, container=True),
        rating_key=title,
        url=url,
        title=title,
        thumb=thumb,
        items=[
            MediaObject(
                parts=[
                    PartObject(
                        key=HTTPLiveStreamURL(url=url)
                    )
                ],
                optimized_for_streaming=True
            )
        ]
    )
    if container:
        return ObjectContainer(objects=[videoClipObject])
    else:
        return videoClipObject


def credentialsAreInvalid(username, password):
    return not username or not password


def displayChannelsNotFetchedWarningMessage(oc):
    oc.message = L('NoChannels')


def displayCredentialsInvalidMessage(oc):
    oc.message = L('NoCredentials')
