docker build . -t falcoeye-workflow --build-arg SSH_KEY="$(cat ssh/id_rsa)"
