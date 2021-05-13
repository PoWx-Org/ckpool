pooldir="/home/opowuser/ckpool" bitcoindir="/home/opowuser/obtc-core/build/scr" uidir="/home/opowuser/obtc-pool-web-ui"

if [ -z "$1" ]
  then
          echo "No first argument(pool's directory). Using default ( $pooldir )"
  else
    echo "Provided pool directory: $1"
fi

if [ -z "$2" ]
  then
    echo "No second argument(bitcoin's directory). Using default ( $bitcoindir )"
  else
    echo "Provided bicoin directory: $2"
fi

if [ -z "$3" ]
  then
    echo "No third argument(pool ui's directory). Using default ( $uidir )"
  else
    echo "provided pool ui's: $3"
fi

echo \
"
[Unit]
Description=oBTC node service
After=network.target
StartLimitIntervalSec=10
StartLimitBurst=5

[Service]
Type=simple
Restart=always
RestartSec=3
User=opowuser
Group=opowuser
WorkingDirectory=$bitcoindir
ExecStart=$bitcoindir/bitcoind -testnet -fallbackfee=0.00000001

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/bitcoind.service

echo \
"
[Unit]
Description=oBTC pool
After=network.target bitcoind.service
StartLimitIntervalSec=10
StartLimitBurst=5

[Service]
Type=simple
Restart=always
RestartSec=3
User=opowuser
Group=opowuser
WorkingDirectory=$pooldir
ExecStart=$pooldir/src/ckpool -c $pooldir/ckpool.conf -l 5

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/obtc-pool.service

echo \
"
[Unit]
Description=oBTC node service
After=network.target obtc-pool.service
StartLimitIntervalSec=10
StartLimitBurst=5

[Service]
Type=simple
Restart=always
RestartSec=3
User=opowuser
Group=opowuser
WorkingDirectory=$pooldir/tools/parser
ExecStart=$pooldir/tools/parser/accounting.sh

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/accounter.service

echo \
"
[Unit]
Description=oBTC pool WEB Interface
After=network.target bitcoind.service obtc-pool.service accounter.sevice
StartLimitIntervalSec=10
StartLimitBurst=5

[Service]
Type=simple
Restart=always
RestartSec=3
User=opowuser
Group=opowuser
WorkingDirectory=$uidir
ExecStart=/usr/bin/npm run start

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/obtc-pool-ui.service


systemctl daemon-reload
systemctl enable bitcoind
systemctl enable obtc-pool
systemctl enable accounter
systemctl enable obtc-pool-ui
systemctl start bitcoind
systemctl start obtc-pool
systemctl start accounter
systemctl start obtc-pool-ui
