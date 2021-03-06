CMD_PACKAGE_NAME := "grpc-server"

build: ## build grpc-server app docker image
	@DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker build -t quay.io/matihost/$(CMD_PACKAGE_NAME):latest -f Dockerfile ../..

push: ## push image to quay.io repository (assume docker login quay.io has been perfomed)
	docker push quay.io/matihost/$(CMD_PACKAGE_NAME):latest


run-server: ## run grpc-server app container
	docker run --detach --name $(CMD_PACKAGE_NAME) -p 6565:6565 --rm quay.io/matihost/$(CMD_PACKAGE_NAME):latest --address :6565

show-server-logs: ## show grpc-server app container logs
	docker logs grpc-server

stop-server: ## stop grpc-server container
	docker rm grpc-server --force

check-readyness: ## check GRPC HealtCheck readyness
	grpc-health-probe -addr :6565

install-grpc-healthcheck: ## install GRPC HealtCheck readyness app
	go get github.com/grpc-ecosystem/grpc-health-probe

help: ## show usage and tasks (default)
	@eval $$(sed -E -n 's/^([\*\.a-zA-Z0-9_-]+):.*?## (.*)$$/printf "\\033[36m%-30s\\033[0m %s\\n" "\1" "\2" ;/; ta; b; :a p' $(MAKEFILE_LIST))
.DEFAULT_GOAL := help
.PHONY: help build run-server
