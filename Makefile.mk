S3_BUCKET=$(S3_BUCKET_PREFIX)-$(AWS_REGION)
S3_OBJECT_ACL=private
ALL_REGIONS=$(shell aws --region $(AWS_REGION) \
		ec2 describe-regions 		\
		--query 'join(`\n`, Regions[?RegionName != `$(AWS_REGION)`].RegionName)' \
		--output text)

VERSION := $(shell git describe  --tags --dirty)

build: target/$(NAME)-$(VERSION).zip		## build the lambda zip file

fmt:	## formats the source code
	black src/ tests/

test:	## run python unit tests
	pipenv run tox

test-record: ## run python unit tests, while recording the boto3 calls
	RECORD_UNITTEST_STUBS=true pipenv run tox

test-templates:     ## validate CloudFormation templates
	for n in ./cloudformation/*.yaml ; do aws cloudformation validate-template --template-body file://$$n ; done

deploy: target/$(NAME)-$(VERSION).zip@$(S3_BUCKET_PREFIX)	## AWS lambda zipfile to bucket

target/$(NAME)-$(VERSION).zip: src/ requirements.txt
	mkdir -p target/content
	docker build --build-arg ZIPFILE=$(NAME)-$(VERSION).zip -t $(NAME)-lambda:$(VERSION) -f Dockerfile.lambda . && \
		ID=$$(docker create $(NAME)-lambda:$(VERSION) /bin/true) && \
		docker export $$ID | (cd target && tar -xvf - $(NAME)-$(VERSION).zip) && \
		docker rm -f $$ID && \
		chmod ugo+r target/$(NAME)-$(VERSION).zip

target/$(NAME)-$(VERSION).zip@$(S3_BUCKET_PREFIX): target/$(NAME)-$(VERSION).zip
	aws s3 --region $(AWS_REGION) \
		cp --acl $(S3_OBJECT_ACL) \
		cloudformation/$(NAME).yaml \
		s3://$(S3_BUCKET)/lambdas/$(NAME)-$(VERSION).yaml
	aws s3 --region $(AWS_REGION) \
		cp --acl $(S3_OBJECT_ACL) \
		target/$(NAME)-$(VERSION).zip \
		s3://$(S3_BUCKET)/lambdas/$(NAME)-$(VERSION).zip
	touch target/$(NAME)-$(VERSION).zip@$(S3_BUCKET_PREFIX)

deploy-all-regions: target/$(NAME)-$(VERSION).zip@$(S3_BUCKET_PREFIX)	## AWS lambda zipfiles to all regional buckets
	@for REGION in $(ALL_REGIONS); do \
		echo "copying to region $$REGION.." ; \
		aws s3 --region $$REGION \
			cp  --acl $(S3_OBJECT_ACL) \
			s3://$(S3_BUCKET)/lambdas/$(NAME)-$(VERSION).zip \
			s3://$(S3_BUCKET_PREFIX)-$$REGION/lambdas/$(NAME)-$(VERSION).zip; \
	done

undeploy-all-regions:	## deletes AWS lambda zipfile of this release from all buckets in all regions
	@for REGION in $(ALL_REGIONS); do \
                echo "removing lamdba from region $$REGION.." ; \
                aws s3 --region $(AWS_REGION) \
                        rm  \
                        s3://$(S3_BUCKET_PREFIX)-$$REGION/lambdas/$(NAME)-$(VERSION).zip; \
        done
	rm -f target/$(NAME)-$(VERSION).zip@$(S3_BUCKET_PREFIX)

Pipfile.lock: Pipfile setup.cfg pyproject.toml
	pipenv update

deploy-provider: target/$(NAME)-$(VERSION).zip@$(S3_BUCKET_PREFIX)  ## deploys the custom provider
	sed -i -e 's^lambdas/$(NAME)-[0-9]*\.[0-9]*\.[0-9]*[^\.]*\.'^lambdas/$(NAME)-$(VERSION).^g cloudformation/$(NAME).yaml
	aws cloudformation deploy \
                --capabilities CAPABILITY_IAM \
                --stack-name $(NAME) \
                --template-file ./cloudformation/$(NAME).yaml \
                --parameter-overrides S3BucketPrefix=$(S3_BUCKET_PREFIX) \
				--no-fail-on-empty-changeset

delete-provider: ## deletes the custom provider
	aws cloudformation delete-stack --stack-name $(NAME)
	aws cloudformation wait stack-delete-complete  --stack-name $(NAME)

deploy-pipeline:  ## deploys the CI/CD deployment pipeline
	aws cloudformation deploy \
                --capabilities CAPABILITY_IAM \
                --stack-name $(NAME)-pipeline \
                --template-file ./cloudformation/cicd-pipeline.yaml \
                --parameter-overrides S3BucketPrefix=$(S3_BUCKET_PREFIX) \
				--no-fail-on-empty-changeset

delete-pipeline:  ## deletes the CI/CD deployment pipeline
	aws cloudformation delete-stack --stack-name $(NAME)-pipeline
	aws cloudformation wait stack-delete-complete  --stack-name $(NAME)-pipeline

deploy-demo:	## deploys the demo stack
	aws cloudformation deploy --stack-name $(NAME)-demo \
		--template-file ./cloudformation/demo.yaml \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

delete-demo: ## deletes the demo stack
	aws cloudformation delete-stack --stack-name $(NAME)-demo
	aws cloudformation wait stack-delete-complete  --stack-name $(NAME)-demo

tag-patch-release: ## create a tag for a new patch release
	pipenv run git-release-tag bump --level patch

tag-minor-release: ## create a tag for a new minor release
	pipenv run git-release-tag bump --level minor

tag-major-release: ## create a tag for new major release
	pipenv run git-release-tag bump --level major

show-version: ## shows the current version of the workspace
	pipenv run git-release-tag show .

help:           ## Show this help.
		@egrep -h ':[^#]*##' $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/:[^#]*##/: ##/' -e 's/[ 	]*##[ 	]*/ /' | \
		awk -F: '{printf "%-20s -", $$1; $$1=""; print $$0}'
