SHORT_NAME ?= slugbuilder

export GO15VENDOREXPERIMENT=1

# Note that Minio currently uses CGO.

LDFLAGS := "-s -X main.version=${VERSION}"
IMAGE_PREFIX ?= koli
BINDIR := ./rootfs/bin

include versioning.mk

SHELL_SCRIPTS = $(wildcard _scripts/*.sh) $(wildcard rootfs/bin/*_object) $(wildcard rootfs/bin/*_cache) rootfs/bin/normalize_storage $(wildcard rootfs/builder/*)

# The following variables describe the containerized development environment
# and other build options
DEV_ENV_IMAGE := quay.io/koli/go-dev:0.2.0
DEV_ENV_WORK_DIR := /go/src/${REPO_PATH}
DEV_ENV_CMD := docker run --rm -v ${CURDIR}:${DEV_ENV_WORK_DIR} -w ${DEV_ENV_WORK_DIR} ${DEV_ENV_IMAGE}
DEV_ENV_CMD_INT := docker run -it --rm -v ${CURDIR}:${DEV_ENV_WORK_DIR} -w ${DEV_ENV_WORK_DIR} ${DEV_ENV_IMAGE}

all: docker-build docker-push

docker-build:
	docker build ${DOCKER_BUILD_FLAGS} -t ${IMAGE} rootfs
	docker tag ${IMAGE} ${MUTABLE_IMAGE}

deploy: docker-build docker-push

test: test-style test-unit

test-style:
	${DEV_ENV_CMD} shellcheck $(SHELL_SCRIPTS)

test-unit:
	docker run --entrypoint /usr/bin/env ${IMAGE} python3 -m unittest procfile

.PHONY: all docker-build docker-push test
