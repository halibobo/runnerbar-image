
网址介绍：https://dahei.me/2018/06/21/python%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E9%A9%AC%E6%8B%89%E6%9D%BE%E5%9B%BE%E7%89%87/#more

### 前言
目前学习python几个月了，由于自己比较喜欢跑马拉松，已经跑过了很多场比赛，前些天就写了个简单的爬虫爬取了网上三千多场马拉松比赛的报名信息。
今年5月27日，我又参加了巴图鲁关门山壹佰越野50公里组的比赛，这里的“巴图鲁”源自蒙古语“英雄”的意思，这场比赛也是出了名的虐，地点在辽宁省本溪市 · 关门山国家森林公园，累计爬升3655m。当天早上六点准时出发，刚跑没多久就来了很长一段陡峭的台阶......此处省略一万字......最终经过很多小时的艰苦奋战完成了比赛。
<!-- more -->
赛后去官网想找几张好看的图片发朋友圈，打开官网赛事图片链接到了爱运动的一个网页[http://runnerbar.com/yd_runnerbar/album/pc?type=3&activity_id=10712](http://runnerbar.com/yd_runnerbar/album/pc?type=3&activity_id=10712)，这是个单页面的网页，不断滚动会自动加载更多的图片，我把页面一点点滚动找了很长一段时间根本找不到我的照片，刷新一下页面照片又从头开始了，实在不能忍。于是，我想要不把图片全部下载到本地查看吧，想干就干。

#### 1. 分析
##### 1.1 Chrome调试
在chrome浏览器里输入快捷键Cmd + Opt + I（Windows上是F12,或Ctrl + Shift + I），将调试选项切到Network，如下
![enter image description here](https://github.com/halibobo/BlogImage/blob/master/blog/batulu/1543910372544_15_59_31__12_04_2018.jpg?raw=true)
一个个观察此网页发送的请求，找到和图片相关的请求
![enter image description here](https://github.com/halibobo/BlogImage/blob/master/blog/batulu/1543910516146_16_01_54__12_04_2018.jpg?raw=true)
这是一个get请求，初步分析里面的参数，activity_id代表赛事id，page和pageSize分别代表页数和每页大小，接着将请求放在postman上印证
![enter image description here](https://github.com/halibobo/BlogImage/blob/master/blog/batulu/1543915583110_17_26_21__12_04_2018.jpg?raw=true)
##### 1.2请求分析
在postman里加了三个参数成功返回了一个json格式的值，第一阶段很顺利，接着分析里面的返回值，下面取了其中的一个元素

    {
    "album": {
        "activity_photo_count": 6984,
        "searchResultList": [
            {
                "id": "32926651",
                "uid": 50392,
                "name": "巴图鲁关东越野",
                "user_name": null,
                "user_img": "http://oss.runnerbar.com/img/user_upload/origin/20180526/1527305285356_fb59065d_18ce_478b_a3aa_259783f4cd5b.jpg",
                "create_time": 1527313780000,
                "image_height": 3648,
                "image_width": 5472,
                "orientation": 1,
                "url_hq": "http://oss.runnerbar.com/img/watermark/user_upload/origin/20180526/1527313783392_235c5cea_5d0c_4cd7_afc6_0ba37cdc7c1d.jpg?quality=h",
                "url_lq": "http://oss.runnerbar.com/img/watermark/user_upload/origin/20180526/1527313783867_7d986351_fde4_418a_8fb3_1723dcb38aec.jpg",
                "content": null,
                "is_like": 0,
                "like_count": null,
                "comment_count": 0
            }}


这是个json格式，最外层里有个album元素，album里包含了图片总数量activity_photo_count和图片信息的数组searchResultList。每张图片包含了id、uid、user_img、create_time等等，和图片路径相关的有三个值分别是user_img、url_hq、url_lq，其中的user_img打开后发现是赛事的宣传logo，剩下的url_hq、url_lq根据命名就很容易猜想到这是对应的两种尺寸的图片，用浏览器分别打开，果不其然正是想要的图片路径。

#### 2.代码
##### 2.1
上面已经知道了请求url和参数，下面就是需要将这些用代码实现出来。首先是发请求

    url='http://m.yundong.runnerbar.com/yd_mobile/share/album.json'
    para = {'activity_id':id,'page':page,'pageSize':100}
    header = {}
    r = requests.post(url,data=para,headers= header)
请求的返回值是json，json内容在上面已经贴出来了这里就不再重复，接着解析这个json

    json_r = r.json()
    parsed_json = json_r['album']['searchResultList']
    activity = {}
    items = []
    count = json_r['album']['activity_photo_count']

这里就取到了图片总数量和图片信息的数组，这个请求参数是page和pageSize，一个请求只能取到一部分图片信息并不能把所有的图片都取出来。那能不能把所有图片分成一页返回呢？于是在postman上做了实验，将page=1，pageSize=10000发送，结果并不是想要的，真正返回的图片数量是100。说明这个接口做了校验，每个分页最大数量是100。看来投机取巧是不行了，分页还是要做的。
首先将单个请求封装成方法，传入page返回对应page的图片信息数组

    def getRaceInfo(id,page):
	    url='http://m.yundong.runnerbar.com/yd_mobile/share/album.json'
	    para = {'activity_id':id,'page':page,'pageSize':100}
	    header = {}
	    r = requests.post(url,data=para,headers= header)
	    json_r = r.json()
	    parsed_json = json_r['album']['searchResultList']
	    activity = {}
	    items = []
	    count = json_r['album']['activity_photo_count']
	    for item in parsed_json:
	        # print(item['user_img'])
	        items.append(item)
	    activity['items'] = items
	    activity['count'] = count
    return activity

图片的做数量是count，每页分100张图片，起点是第1页，那么总的分页数量就是count/100+2，分页的代码就应该是这样的

    for i in range(1,int(count/100+2)):
	    data = getRaceInfo(id,i)['items']
这里只是贴了一小段代码，完整代码可以参见上面的github地址

#### 2.2 下载

有了图片在url，下载图片就更简单了，直接上代码

    def save_img(img_url,file_name,file_path='book'):
    #保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    try:
        if not os.path.exists(file_path):
            print('文件夹',file_path,'不存在，重新建立')
            #os.mkdir(file_path)
            os.makedirs(file_path)
        #获得图片后缀
        file_suffix = os.path.splitext(img_url)[1]
        #拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path,os.sep,file_name,file_suffix)
       #下载图片，并保存到文件夹中
        urllib.request.urlretrieve(img_url,filename=filename)
    except IOError as e:
        print('文件操作失败',e)
    except HTTPError as e:
        print('Error code: ', e.code)
    except Exception as e:
        print('错误 ：',e)
运行python，查看本地文件
几千张图片很快下载到了本地
![enter image description here](https://github.com/halibobo/BlogImage/blob/master/blog/batulu/1543918174039_18_09_31__12_04_2018.jpg?raw=true)
这时又有了新的想法，既然可以下载关门山越野的图片，是不是可以把爱运动里所有的图片都下载下来，说干就干。于是我将赛事id定义成参数，写个方法遍历id。改动了几行从新运行，几个小时后程序还在运行但是图片占用的大小已经超过了7G，
![enter image description here](https://github.com/halibobo/BlogImage/blob/master/blog/batulu/1543918536552_18_15_35__12_04_2018.jpg?raw=true!%5BAlt%20text%5D%28./1543918858425.png%29)
打开文件里面包含了各个赛事的图片，眼看图片越来越多加上我的mac存储空间有限最终停止了下载，但是这个思路应该是可行的。

源码地址： https://github.com/halibobo/runnerbar-image

### 最后
整个过程从开始到结束都在一天内完成的，代码里也没有什么复杂的逻辑，但完成之后心里还是有很多的满足感，哈哈....让我骄傲一会  。。。
贴上完赛信息
![enter image description here](https://github.com/halibobo/BlogImage/blob/master/blog/batulu/mmexport1528499659901.jpg?raw=true)


最后贴上一句我很喜欢的赛事宣传语

		和一群志同道合的人，一起奔跑在理想的路上，
		回头有一路的故事，低头有坚定的脚步，抬头有清晰的远方。
		                                —— 致巴图鲁er



