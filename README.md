# vManRaki a project to help vManage to Meraki migrations.

This project has two functions:

1) Takes existing vEdge configuration, outputs a flat excel file of edge devices deployed w/ interface config.
Run:
  vmanage_datagrab.py

It is hardcoded to the Devnet SD-WAN demo environment at the moment.

3) Take the flat file and create a Meraki dashboard with the same configuration.

Configure Environment Variables:
  MERAKI_DASHBOARD_API_KEY
  ORG_ID

Run:
  meraki_push.py

And it will create networks. The operation isn't intelligent, so it'll try to create networks no matter what. If you've run this once, you'll have to delete networks to run it again.
