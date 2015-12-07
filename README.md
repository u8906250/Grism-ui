# Grism-ui
Grism UI

## introduction
採用 python web framework (ex. web2py)，建立前後端並用來控制 Grism 系統


Grism 功能包含 L2-L7層封包過濾、Network tap、Load Balance、packet tunnel/de-tunnel/stripping/tagging/masking 等，產品說明請參考 http://packetx.biz/grism.htm

可參考現有介面開發 http://grism.ddns.net:8080/grism packetx/packetx，主要有三個頁面，登入頁面、設定頁面、流量頁面

#後端
## 設定方法
在 /data/ftproot 目錄下產生 run.xml 檔案，內容包含所有的設定，再產生 run.xml.ok 檔案即完成設定。如設定檔案執行正確，該目錄下會出現 ok1 檔案，並且會將 run.xml 移到 /data/ftproot/running-config 目錄下，如果執行失敗，該目錄下會出現 ok2 檔案

## run.xml
[xml-format.md](dev-doc/xml-format.md)

## config.json
[config.md](dev-doc/config.md)

## statistics
在 /data/ftproot 目錄下，記錄目前所有 input , output 的流量，每5秒會更新一次

其中 port 欄位代表的是 input 的 idx 可參考 config.md 的說明，

example
```
port,inErrors,inDrops,inPackets,inBytes,inMbps,outDrops,outPackets,outBytes,outMbps
0,0,0,3136232,4316017374,58.54,0,0,0,0.00
1,0,0,0,0,0.00,0,3136232,4316017374,58.54
2,0,0,0,0,0.00,0,0,0,0.00
3,0,0,0,0,0.00,0,0,0,0.00
4,0,0,0,0,0.00,0,0,0,0.00
5,0,0,0,0,0.00,0,0,0,0.00
6,0,0,0,0,0.00,0,0,0,0.00
7,0,0,0,0,0.00,0,0,0,0.00
8,0,0,0,0,0.00,0,0,0,0.00
9,0,0,0,0,0.00,0,1662,1071107,0.01

```

#前端
![polices](dev-doc/grism_ui_policies (1).png)
![polices new1](dev-doc/grism_ui_policies_new_1 (2).png)
![polices new2](dev-doc/grism_ui_policies_new_2 (3).png)
![polices new3](dev-doc/grism_ui_policies_new_3 (4).png)
![polices new4](dev-doc/grism_ui_policies_new_4 (5).png)
