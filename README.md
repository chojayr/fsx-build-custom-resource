## fsx-build-custom-resource

An automation to build the FSx share volume using the [CloudFormation Custom Resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html "AWS CloudFormation Custom Resource") and Python Library [custom-resource-helper](https://github.com/aws-cloudformation/custom-resource-helper "custom-resource-helper")

---
### Why using a CloudFormation Custom Resource? 

As of now the FSx is still in the early stage and the AWS FSx release the support of using the ["SelfManagedActiveDirectory"](https://aws.amazon.com/about-aws/whats-new/2019/06/amazon-fsx-for-windows-file-server-now-enables-you-to-use-file-systems-directly-with-your-organizations-self-managed-active-directory/), before it only support the use of AWS DFS, the AWS FSx(Windows) CloudFormation does not support(for now, soon it will be supported) the configuration of the "SelfManagedActiveDirectory" and the only way to provision the FSx share volume with self managed active directory support on CloudFormation is by use the CloudFormation Custom Resource 


---
### Components

* fsx-build-function - Components to deploy the required IAM permission, Lambda Function and CloudWatch Logs that will be use by the fsx-build-resource
* fsx-build-resource - Components to deploy the custom resource stack 
* encrypt_value.py - To encrypt the AD user password before putting it to the parameter file

---
### How to use?

Please check more details here - [Deploy AWS FSx with 'SelfManagedActiveDirectory' on CloudFormation using fsx-build-custom-resource](http://chojayr.github.io/2019-08-24-fsx-build-custom-resource "deploy fsx-build-custom-resource")



