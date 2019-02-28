Simple python script that downloads and applies the [firehol level 1 blacklist](https://iplists.firehol.org/files/firehol_level1.netset) on an ipfire machine.

The script applies every CIDR inside the firehol blacklist, except 192.168.0.0/16 and 127.0.0.0/8 (to prevent us from locking ourselves out of our own ipfire machine).

#Howto install

* download the `firehol-downloader.py` script to the `/usr/bin/` folder on your ipfire machine
* make the script executable with `chmod u+rx /usr/bin/firehol-downloader.py`

* connect via SSH to your ipfire machine and modify `/etc/sysconfig/firewall.local`. 
Add the following lines to the `start` condition of your `firewall.local` file:
```
    /sbin/iptables -I CUSTOMFORWARD -m set --match-set firehol dst -j REJECT
    /sbin/iptables -I CUSTOMINPUT -m set --match-set firehol src -j REJECT
    /sbin/iptables -I CUSTOMOUTPUT -m set --match-set firehol dst -j REJECT
```

Add the following lines to the `stop`condition your `firewall.local` file:
```
    /sbin/iptables -F CUSTOMFORWARD
    /sbin/iptables -F CUSTOMINPUT
    /sbin/iptables -F CUSTOMOUTPUT
```

The resulting `/etc/sysconfig/firewall.local` file should now look similar to this one: 

```
    #!/bin/sh
    # Used for private firewall rules

    # See how we were called.
    case "$1" in
      start)
        ## add your 'start' rules here
        /sbin/iptables -I CUSTOMFORWARD -m set --match-set firehol dst -j REJECT
        /sbin/iptables -I CUSTOMINPUT -m set --match-set firehol src -j REJECT
        /sbin/iptables -I CUSTOMOUTPUT -m set --match-set firehol dst -j REJECT
        ;;
      stop)
        ## add your 'stop' rules here
        /sbin/iptables -F CUSTOMFORWARD
        /sbin/iptables -F CUSTOMINPUT
        /sbin/iptables -F CUSTOMOUTPUT
        ;;
      reload)
        $0 stop
        $0 start
        ## add your 'reload' rules here
        ;;
      *)
        echo "Usage: $0 {start|stop|reload}"
        ;;
    esac
```

* create a new cronjob entry with `fcrontab -e` which calls the `firehol-downloader.py` script periodically. 
  If you want to check for new firehol blacklists once per day, add the following entry: 
  `0 1 * * * python /usr/bin/firehol-downloader.py`
