# Grism-ui
Grism UI

## introduction
採用 python web framework (ex. web2py)，建立前後端並用來控制 Grism 系統


Grism 功能包含 L2-L7層封包過濾、Network tap、Load Balance、packet tunnel/de-tunnel/stripping/tagging/masking 等，詳細內容請參考 http://packetx.biz/grism.htm

## 控制方法
在 /data/ftproot 目錄下產生 run.xml 檔案，內容包含所有的設定，再產生 run.xml.ok 檔案即完成設定。如設定檔案執行正確，該目錄下會出現 ok1 檔案，並且會將 run.xml 移到 /data/ftproot/running-config 目錄下，如果執行失敗，該目錄下會出現 ok2 檔案

## run.xml
[xml-format.md](xml-format.md)

## config.json
系統設定檔案，在 /data/ftproot 目錄下會有一份副本，後端可以讀取這的檔案來取得系統的資訊，其中最主要的就是這台機器有哪些介面可以做 input 以及 output

[config.md](config.md)
