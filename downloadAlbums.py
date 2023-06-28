import os
import urllib.request
import logging
import requests
from pprint import pprint
from vkapi import VkApi

import config

def getPhotoUrls(photos):
    photoUrls = []
    for photoItem in photos:
        sizes = photoItem.get('sizes')
        if sizes:
            maxAvailSize = max(sizes, key=lambda x: x['width'])
            photoUrls.append(maxAvailSize['url'])
    return photoUrls

def writeUnavailablePhoto(file):
    with open('unavailable_photos.txt', 'a') as f:
        f.write(file + '\n')


def downloadPhotos(outDir, urls):
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    total_photos = len(urls)
    downloaded_count = 0  # Счетчик скачанных фотографий
    for i, photoUrl in enumerate(urls, start=1):
        file = os.path.join(outDir, photoUrl.rsplit('/', 1)[-1])
        if not os.path.exists(file):
            response = requests.head(photoUrl)
            if response.status_code == 200:
                urllib.request.urlretrieve(photoUrl, file)
                downloaded_count += 1
            else:
                print("Фотография недоступна")
                writeUnavailablePhoto(photoUrl)

    if downloaded_count > 0:
        print(f"Скачивание фотографий из альбома завершено ({downloaded_count} из {total_photos} скачано)")
    else:
        print("Вы уже скачали фотографии")



#logging.basicConfig(level=logging.DEBUG)

api = VkApi(config.ACCESS_TOKEN)
users = api.getUsersByUids(config.UIDS)
for user in users:
    userId = user['id']
    userName = '%s %s' % (user['first_name'], user['last_name'])
    albums = api.getUserAlbums(userId)

    print('%s (%d) - %d albums' % (userName, userId, len(albums)))

    for album in albums:
        outDir = os.path.join(config.OUT, '%s (%d)' % (userName, userId),
                              album['title'] + ' (' + str(album['id']) + ')')

        print('    "%s" - %d photos' % (album['title'], album['size']))

        choice = input("Хотите скачать фотографии из данного альбома? (y/n): ")
        if choice.lower() == 'y':
            photoUrls = getPhotoUrls(api.getPhotosFromAlbum(album))
            if photoUrls:
                print(f"Начато скачивание фотографий из альбома: {album['title']}")
                downloadPhotos(outDir, photoUrls)
                print(f"Скачивание фотографий из альбома {album['title']} завершено")
            else:
                print(f"Альбом {album['title']} не содержит фотографий")
        else:
            print(f"Пропускаем скачивание фотографий из альбома: {album['title']}")




