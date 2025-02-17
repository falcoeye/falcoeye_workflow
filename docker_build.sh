# Point your shell to minikube's Docker daemon
eval $(minikube docker-env)
docker build . -t falcoeye-workflow
