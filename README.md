# Backend p2p miniapp v 0.1

## Security key

```bash
mkdir security && cd security
openssl genrsa -out api.pem 2048
openssl rsa -in api.pem -pubout -outform PEM -out api.crt
cd ..
```
