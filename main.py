#!/usr/bin/env python
#-*-coding:utf-8-*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.api import xmpp
import webapp2
import urllib2
import urllib
import re

class XMPPHandler(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        msg = message.body.encode('UTF-8')
        prefix = msg[0:3].lower()
        content = msg[3:]
        prefix_list = {
            '-tq': 'weather',
        } 
        subfix = prefix_list.get(prefix, 'other')
        func = getattr(self, 'query_' + subfix)
        message.reply(func(content))

    def get(self):
        print self.query_weather('上海')

    def query_weather(self, content):
        try:
            user_agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.47 Safari/536.11'
            param = '天气 ' + content
            url = 'http://www.soso.com/q?' \
                + urllib.urlencode({'sc':'web','w':param})
            request = urllib2.Request(url)
            request.add_header('User-Agent', user_agent)
            request.add_header('Accept-Charset', 'UTF-8,*;q=0.5')
            response = urllib2.urlopen(request)
            html = response.read()
            regex = re.compile(r'<div class="bo_58_lis"><dl>(.*?)</dl></div>')
            ret = regex.search(html)
            if not ret:
                raise '暂时没有%s的天气预报' % content
            ret = ret.group(1)
            ret = ret.decode('gbk').encode('utf8')
            weather = re.compile(u'<dd.*?title="([^"]+)">\s*<span>([^<]+)</span>.*?<span>([^<]+)<em>.*?<span\s+class="bo_58_w"\s*>([^<]+)')
            ret = weather.findall(ret)
            #ret_list = []
            #for row in ret:
                #wind, day, temp, sun = row
                #ret_list.append(' '.join([day, temp, sun, wind]))
            #return "\n\n".join(ret_list)
            ret_str = ''
            for row in ret:
                wind, day, temp, sun = row
                ret_str += '%s %s %s %s' % (day, temp, sun, wind)
                ret_str += "\n\n"
            return ret_str
        except urllib2.HTTPError, e:
            return 'error:' + e.code

    def query_other(self, content):
        return '无效的命令'


app = webapp2.WSGIApplication([
    ('/_ah/xmpp/message/chat/', XMPPHandler),
    ('/__test_weather__', XMPPHandler)
    ], debug=True)
