# DPA Calculator

## How to run
### Local python
#### Setup and install
1. Setup a [venv](https://docs.python.org/3/library/venv.html) for the project.
2. Follow the setup and installation procedure in the README in the root directory.
3. Install additional project requirements run `pip install -r requirements.txt`
4. If you are planning on developing, install the test requirements with `pip install -r test-requirements.txt`

#### Run
1. Change your working directory to `src/harness`
2. Include the `harness` directory in your python path
   1. Max/Linux
       ```shell
       export PYTHONPATH=$PYTHONPATH;$(pwd)
       ```
   2. Windows CMD
       ```shell
       set PYTHONPATH=%PYTHONPATH%;%cd% 
       ```
3. Run the main entrypoint
    ```shell
    python3 cu_pass/dpa_calculator/main.py -h
    ```

#### Test
Tests are in `src\harness\testcases\cu_pass\dpa_calculator`, using [Behave](https://behave.readthedocs.io/en/stable/)
and [Pytest](https://docs.pytest.org/en/7.1.x/).

### Docker
Install Docker

#### Build
From the root directory, run
```shell
docker build . -f src/harness/cu_pass/dpa_calculator/Dockerfile -t dpa
```

#### Run
Mount data directory volumes and use environment variables matching the container volume paths.

```shell
docker run \
  --env AWS_ACCESS_KEY_ID=<aws_access_key_id>
  --env AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
  --env AWS_DEFAULT_REGION=<aws_region>
  -v "<PATH_TO_LOCAL_COMMON_DATA>:/cu_pass/Common-Data" \
  dpa
```

### AWS
#### Push docker image
##### Setup
- Ensure the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) is installed.

##### Set AWS repository variable
- Mac/Linux
    ```shell
    export AWS_REPO=<aws_account_id>.dkr.ecr.<aws_region>.amazonaws.com
    export AWS_REGISTRY=$AWS_REPO/dpa_calculator:latest
    ```

- Windows
    ```shell
    set AWS_REPO <aws_account_id>.dkr.ecr.<aws_region>.amazonaws.com
    set AWS_REGISTRY $AWS_REPO/dpa_calculator:latest
    ```

##### ECR
- Login
    ```shell
    aws ecr get-login-password | docker login --username AWS --password-stdin "$AWS_REPO"
    ```
- Push
    ```shell
    docker tag dpa "$AWS_REGISTRY"
    docker push "$AWS_REGISTRY"
    ```

#### EC2 Instance
1. Launch EC2 instance with 20 GB of memory
2. Attach Common-Data volume to instance
   1. [Format](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html) and mount the volume
       - Example
         ```shell
         lsblk
         sudo mkdir /Common-Data
         sudo mount /dev/xvdf /Common-Data
         ```
      
3. SSH into the instance
   ```shell
   ssh -i <ssh_key_path> ec2-user@<instance_ip_address>
   ```
4. [Install](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html) Docker
   ```shell
   sudo yum update -y
   sudo amazon-linux-extras install docker
   sudo yum install docker
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   ```
5. Disconnect and SSH back into the instance
6. Setup AWS config
   ```shell
    aws configure
    ```
7. Set overcommit mode
   1.  Command
       ```shell
       echo 1 | sudo tee /proc/sys/vm/overcommit_memory
       ```
   2. Resources
      1. https://stackoverflow.com/a/57511555/3869199
      2. https://forums.aws.amazon.com/message.jspa?messageID=950215
8. Log in using the ECR login command above
9. Run the docker image with the command above and the image in the ECR repo
    ```shell
    docker run -it \
      --env AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id) \
      --env AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key) \
      --env AWS_DEFAULT_REGION=$(aws configure get region) \
      -v "/Common-Data:/cu_pass/Common-Data" \
      <ecs_image>
    ```