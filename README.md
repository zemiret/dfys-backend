# DFYS-backend 

## Building
You need to have *Docker* and *docker-compose* installed.
After that, all you have to do is:
```
docker-compose build
docker-compose up
```

## Testing
```
./scripts/run_tests.sh
```

## Development
If you want to, you can replicate docker environment locally but you don't have to.
To run any command within docker container context, just do:
```
docker-compose run app <your command here>
```

