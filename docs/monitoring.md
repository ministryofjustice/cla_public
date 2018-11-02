# Monitoring

## Logs

Currently, logs on our environments (staging, production) are inside the running containers, in the following folders:

- `/var/log/cla_public`
- `/var/log/nginx`
- `/var/log/wsgi`

To access these, log into the box:

```
$ ssh <your github username>@<IP address of the instance>
$ sudo docker exec -ti cla_public bash
$ tail -f /var/log/cla_public/* /var/log/nginx/* /var/log/wsgi/*
```
