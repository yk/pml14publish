import flickr_api as flickr
import ConfigParser,os,json,itertools,copy

configFileName = "getimages.config"

def getMetaData(photo):
    photo.load()
    tags = photo.tags
    notes = photo.notes
    comments = photo.getComments()
    exif = []
    try:
        exif = photo.getExif()
    except flickr.flickrerrors.FlickrAPIError:
        print 'photo %s does not permit access to exif' % photo.id
    favorites = photo.getFavorites()
    md = copy.deepcopy(photo.__dict__)
    del md['owner']
    md['tags'] = [dict(id=t.id,text=t.text,raw=t.raw) for t in tags]
    md['notes'] = [dict(id=n.id,text=n.text,x=n.x,y=n.y,w=n.w,h=n.h) for n in notes]
    md['comments'] = [dict(id=c.id,text=c.text,datecreate=c.datecreate) for c in comments]
    md['exif'] = [dict(tag=e.tag,raw=e.raw) for e in exif]
    md['favorites'] = []
    for f in favorites:
        try:
            fdict = dict(id=f.id,username=f.username,ispro=f.ispro)
            md['favorites'].append(fdict)
        except flickr.flickrerrors.FlickrAPIError:
            print 'user of favorite %s not found' % f.id

    return md

def savePhoto(photo,path=".",size_label="Medium",want_img=1):
    filename = path + '/' + photo.id 
    imgfilename = filename + '.jpg'
    mdfilename = filename + '.meta'
    if want_img>0:
        print 'saving photo %s in size %s' % (photo.id,size_label)
        if not os.path.isfile(imgfilename):
            photo.save(imgfilename,size_label=size_label)
        else:
            print 'photo %s already exists' % photo.id
    if not os.path.isfile(mdfilename):
        print 'getting metadata for photo %s' % photo.id
        md = getMetaData(photo)
        with open(mdfilename,'w') as f:
            json.dump(md,f,separators=(',',':'),sort_keys=True,indent=4)
    else:
        print 'metadata for photo %s already exists' % photo.id
        
def downloadImages(count,startpage,folder,size_label,want_img,**query):
    page = startpage
    totalpages = startpage
    cnt = 0
    while page <= totalpages and cnt < count:
        rsp = flickr.Photo.search(media='photos',page=page,**query)
        ccnt = min(count-cnt,len(rsp))
        for p in rsp[:ccnt]:
            savePhoto(p,folder,size_label,want_img)
        totalpages = rsp.info.pages
        cnt += ccnt
        page += 1

    print 'downloaded %d images' % cnt

def initApi(apikey,secret):
    flickr.set_keys(api_key=apikey,api_secret=secret)

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read(configFileName)
    query = dict(config.items('Query'))
    count = config.getint('Download','count')
    folder = config.get('Download','folder')
    startpage = config.getint('Download','startpage')
    size_label = config.get('Download','sizelabel')
    want_img = config.getint('Download','wantimg')
    apikey = config.get('Keys','apikey')
    secret = config.get('Keys','secret')
    initApi(apikey,secret)
    downloadImages(count,startpage,folder,size_label,want_img,**query)
    

