# Set path for AWS API tools packages

export AWS_PATH=/opt/aws
export PATH=$PATH:/opt/aws/bin
export JAVA_HOME=/usr/lib/jvm/jre
# uncomment this line to specify AWS_CREDENTIAL_FILE_PATH
#export AWS_CREDENTIAL_FILE=/opt/aws/credentials.txt
[ -d $AWS_PATH/amitools/ec2 ] && source $AWS_PATH/amitools/ec2/environment.sh
for aws_product in ec2 elb rds as mon iam cfn; do [ -d $AWS_PATH/apitools/$aws_product ] && source $AWS_PATH/apitools/$aws_product/environment.sh; done
