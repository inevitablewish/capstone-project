# Simplilearn Capstone Project

##
## Infrastructure Optimization

## (Course-end Project 1)

# Table of Contents

[Project Description 3](#_Toc133485797)

[Project Deliverables 3](#_Toc133485798)

[Project requirements 3](#_Toc133485799)

[Prerequisites 3](#_Toc133485800)

[Solution 4](#_Toc133485801)

[Setting up the Environment 4](#_Toc133485802)

[Ansible Playbook 5](#_Toc133485803)

[Application 5](#_Toc133485804)

[Setting up RBAC for a new user 5](#_Toc133485805)

[ETCD Backup 8](#_Toc133485806)

[Horizontal Pod Auto-scaler 8](#_Toc133485807)

[Load Testing 9](#_Toc133485808)

[Reference 11](#_Toc133485809)

# Project Description

Create a DevOps infrastructure for an e-commerce application to run on high-availability mode.

Background of the problem statement:

A popular payment application,  **EasyPay ** where users add money to their wallet accounts, faces an issue in its payment success rate. The timeout that occurs with
 the connectivity of the database has been the reason for the issue.
 While troubleshooting, it is found that the database server has several downtime instances at irregular intervals. This situation compels the company to create their own infrastructure that runs in high-availability mode.

Given that online shopping experiences continue to evolve as per customer expectations, the developers are driven to make their app more reliable, fast, and secure for improving the performance of the current system.

# Project Deliverables

1. You need to document the steps and write the algorithms in them.
2. The submission of your GitHub repository link is mandatory. In order to track your tasks, you need to share the link of the repository.
3. Document the step-by-step process starting from creating test cases, then executing them, and recording the results.
4. You need to submit the final specification document, which includes:
  1. Project and tester details
  2. Concepts used in the project.
  3. Links to the GitHub repository to verify the project completion.
  4. Your conclusion on enhancing the application and defining the USPs (Unique Selling Points)

# Project requirements

1. Create the cluster (EC2 instances with load balancer and elastic IP in case of AWS)
2. Automate the provisioning of an EC2 instance using Ansible or Chef Puppet
3. Install Docker and Kubernetes on the cluster.
4. Implement the network policies at the database pod to allow ingress traffic from the front-end application pod.
5. Create a new user with permissions to create, list, get, update, and delete pods.
6. Configure application on the pod.
7. Take snapshot of ETCD database
8. Set criteria such that if the memory of CPU goes beyond 50%, environments automatically get scaled up and configured.

# Prerequisites

1. EC2
2. Kubernetes
3. Docker
4. Ansible or Chef or Puppet
5. Terraform (Infrastructure Provisioning)

# Solution

In previous sections we have laid out the requirements and objective of the problem we want to solve. Ideally, it is required to have highly available infrastructure that scales out as the CPU memory consumption crosses 50%.

I have decided to use Amazon Web Services as public cloud service provider to provision the required infrastructure. To provision the infrastructure in AWS, I have used Terraform. A more detailed information about terraform can be found on [Hasicorp website](https://developer.hashicorp.com/terraform/intro)[1].

Terraform creates necessary components of the infrastructure i.e., Servers (Ec2 Instances), the network required to communicate between the servers, the Virtual Private Cloud where these components reside and control the type of communication it can allow using Security Groups and Firewalls.

Terraform works in parallel with ansible i.e., a configuration management tool that is used to configure the provisioned servers and set up master / worker environment. Ansible further helps in installing Kubernetes, Docker and the respective network layers required to set up Kubernetes Cluster in this Master / Worker env. More details about ansible are found from its [website](https://www.ansible.com/)[2].

## Setting up the Environment

I have used the [following github repository](https://github.com/lkravi/kube8aws.git)[3] as primary source and modified it according to my needs. The environment set up is reflected in the following architecture diagram.

![](RackMultipart20230427-1-jf3tsr_html_31fbb3ed25742197.png)

_Figure 1 Architecture Diagram of Environment Setup_

3 ec2-instances are created using terraform that is accessible from the following [github repository](https://github.com/inevitablewish/simply-learn-capstone-project)[4]. These instances are distributed across the availability zones in Public Subnets. The choice of using public subnet was made for ease of access to these instances. There is room of improvement to secure the Master and worker nodes.

At the time of provisioning the Masters ec2- instance user data is boot strapped at the time of provisioning of the instance that creates a user called Ubuntu, creates public/private key pair to access worker nodes and importantly installing Ansible for configuration management.

I have used terraform ansible\_helper.tf to firstly export the list of ec2-instance private IP and DNS and save them into local directory under ansible folder named ansible\_vars\_file.yml. This will help the ansible playbook to use the variables declared in ansible\_vars\_file.yml connecting through SSH to worker nodes by running the ansible template to configure the Master and Worker Nodes to use as Kubernetes Cluster.

## Ansible Playbook

The ansible playbook named play.yaml is used to install the basic utilities required to setup Kubernetes cluster. This process is duly automated through ansible. This playbook establishes the environment as Master/worker configuration. In my case, I have used 1 Master node and 2 Worker Nodes where the Master nodes manages the worker nodes and provides full control of the Kubernetes cluster.

With successful completion of playbook, the following 3 requirements are fully met

1. Create the cluster (EC2 instances with load balancer and elastic IP in case of AWS)
2. Automate the provisioning of an EC2 instance using Ansible or Chef Puppet
3. Install Docker and Kubernetes on the cluster.

## Application

I have used a basic application that uses the front end to consume data and saves it into MongoDB database. Such an app was readily available from [educka github](https://github.com/lerndevops/educka.git)[5] repository. The app is slightly modified to meet project requirements.

The next objective is to create a new user with restricted permissions to manage Kubernetes cluster. The user is named ask user1. Since working in AWS environments and Master Node being in Public Subnet, it is required to establish remote connection to the Master Node using SSH. Once the connection is established, a new user is created within Kubernetes that can access the cluster with limited permissions i.e. to get, create, delete, list pods within a cluster.

The process of creating such a user is listed below:

## Setting up RBAC for a new user

There are two requirements to set up the user in Kubernetes i.e., Authenticating a user as listed below and authorizing the user to perform action within the Kubernetes cluster.

For Authentication,

1. create a user called user1

mkdir -p /home/ubuntu/certs && cd /home/ubuntu/certs

1. Create The User Credentials

Kubernetes does not have API Objects for User Accounts. Of the available ways to manage authentication. we will use OpenSSL certificates for their simplicity.

The necessary steps are:

  1. Create a private key for your user. In this case, I will name the file user1.key:

openssl genrsa -out user1.key 2048
 Output:

root@kube-master:/home/certs# openssl genrsa -out user1.key 2048

Generating RSA private key, 2048 bit long modulus (2 primes)

........................+++++

.................+++++

e is 65537 (0x010001)

  1. Create a certificate sign request user1.csr using the private key we just created (user1.key in this example). Make sure you specify your username and group in the -subj section (CN is for the username and O for the group).

openssl req -new -key user1.key -out user1.csr -subj "/CN=user1/O=devops"

  1. Locate Kubernetes cluster certificate authority (CA). This will be responsible for approving the request and generating the necessary certificate to access the cluster API. Its location is normally /etc/kubernetes/pki/ca.crt


  2. Generate the final certificate user1.crt by approving the certificate sign request, user1.csr, we made earlier.

sudo openssl x509 -req -in user1.csr -CA /etc/Kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out user1.crt -days 1000 ; ls -ltr

**Output** :

Signature ok

subject=CN = user1, O = devops

Getting CA Private Key

total 12

-rw------- 1 root root 1679 Jan 8 01:44 user1.key

-rw-r--r-- 1 root root 915 Jan 8 01:47 user1.csr

-rw-r--r-- 1 root root 1017 Jan 8 01:52 user1.crt

1. Create kubeconfig file for the user1.

  1. Add cluster details to configuration file:

kubectl config --kubeconfig=user1.conf set-cluster kubernetes --server=https://{MASTER-DNS}:6443 --certificate-authority=/etc/kubernetes/pki/ca.crt

  1. Add user details to your configuration file:

kubectl config --kubeconfig=user1.conf set-credentials user1 --client-certificate=/home/ubuntu/certs/user1.crt --client-key=/home/ubuntu/certs/user1.key

  1. Add context details to your configuration file:

kubectl config --kubeconfig=user1.conf set-context user1 --cluster=kubernetes--namespace=default --user=user1

  1. Set user1 context for use:

kubectl config --kubeconfig=user1.conf use-context user1

  1. validate Access to API Server:

kubectl --kubeconfig certs/user1.conf version --short

Output:

Client Version: v1.17.0

Server Version: v1.17.0

1. For Authorization, we need to create a cluster role that scopes pods in a cluster with permissions as advised in the project requirements. A yaml file for such a cluster role looks like this:

kind: ClusterRole

apiVersion: rbac.authorization.k8s.io/v1

metadata:

  name: eks-cluster-role

  namespace: default

rules:

- apiGroups:

  - ""

  resources:

  - 'pods'

  verbs:

  - get

  - list

  - update

  - create

  - delete

1. This role is required to be bound with a user i.e., essentially the user I created in step 3 above. The respective yaml file for such a role binding looks like:

---

kind: ClusterRoleBinding

apiVersion: rbac.authorization.k8s.io/v1

metadata:

  name: eks-cluster-rolebinding

  namespace: default

subjects:

- kind: User

  name: user1

  apiGroup: ""

roleRef:

  kind: ClusterRole

  name: eks-cluster-role

  apiGroup: rbac.authorization.k8s.io

1. With access to Master Node through SSH, we can try to attempt to list the pods to confirm Authentication and Authorization works for the user created as user1. Following snip reflects a successful set up of user with limited permissions i.e., user1 cannot list services running in Kubernetes cluster but can only list, create, get and delete pods within the cluster.

![](RackMultipart20230427-1-jf3tsr_html_a2e1c7e8e221065b.png)

_Figure 2 Setting up Context and testing user1 limitations._

## ETCD Backup

As part of deliverable, it is required to create a backup for of your Kubernetes state in case of disaster where recovery is required. Etcd serves as a data base for Kubernetes cluster and when etcd is not available or got corrupt, Kubernetes cluster becomes unmeaningful and the application goes down. To avoid such a situation, it is recommended to create a backup.

To create etcd back up, I need to install command line interface called "etcdctl" that helps to creates the back up and restore it when required.

For creating back up, following script can be used:

ETCDCTL\_API=3 etcdctl \

--endpoints 127.0.0.1:2379 \

--cert /etc/kubernetes/pki/etcd/server.crt \

--key /etc/kubernetes/pki/etcd/server.key \

--cacert /etc/kubernetes/pki/etcd/ca.crt \

snapshot save /opt/backup/etcd-snapshot-latest.db

to restore the etcd,

ETCDCTL\_API=3 etcdctl \

--initial-cluster etcd-restore=https://127.0.0.1:2380 \

--initial-advertise-peer-urls=https://127.0.0.1:2380 \

--name etcd-restore \

--data-dir /var/lib/etcd \

snapshot restore /opt/backup/etcd-snapshot-latest.db

## Horizontal Pod Auto-scaler

Horizontal Pod auto-scaler is used to scale out the application as the resource consumptions goes beyond a threshold. In our case, the threshold is required to be 50% of the cpu memory. This requirement has been specified in the Application Deployment manifest and scaling is carried out through HPA. The HPA yaml file looks like this:

---

kind: HorizontalPodAutoscaler

apiVersion: autoscaling/v2

metadata:

name: springboot-app-hpa

namespace: default

spec:

minReplicas: 2

maxReplicas: 10

scaleTargetRef:

name:  springboot-app

kind: Deployment

apiVersion: apps/v1

metrics:

- type: Resource

resource:

name: memory

target:

type: Utilization

averageUtilization: 50

whenever the average memory utilization crosses 50% of the quota, the application starts to scale out. This can be tested by increasing the load to the application and monitor the resource utilization. I have used K9s to monitor the resource utilization and Kubernetes-dashboard to look for any errors or issues.

## Load Testing

To confirm the autoscaling works when the memory utilization for frontend app goes beyond 50%. I have written a python script that leverages selenium and feeds the data into the app through web interface that in turn increases the load on the application causing the pods to scale out. Before the load is applied to the app, it looks like this:

![](RackMultipart20230427-1-jf3tsr_html_1a3e95dd0017ce18.png)

_Figure 3 Memory Utilization before start of load testing_

As can be seen in the snip above, there are 2 replicas of front-end applications that is default setting and resource consumption currently sits at 50%.

When the script load testing is run by providing the worker node IP / port number http://PublicIP: {service port number} / http://PublicDNS:{service port number} in the python script as reflected below:

![](RackMultipart20230427-1-jf3tsr_html_aa9eed6f94f3b1a.png)

_Figure 4 Highlighting the Worker Node Public IP and Service Port_

It will open the browser and start inserting the random data to increase the load. When monitoring the application after the script is run, it can easily be identified the springboot app pods are increasing in the numbers. This is reflected in series of snips captured below:

![](RackMultipart20230427-1-jf3tsr_html_1630ee6f679aa28.png)

_Figure 5 Memory Utilization at the beginning of load testing_

![](RackMultipart20230427-1-jf3tsr_html_15b88458f709b3c.png)

_Figure 6 Pods scaling out as Memory Utilization crosses 50%_

![](RackMultipart20230427-1-jf3tsr_html_e09736481d50fee0.png)

_Figure 7 Pods scaling out as Memory Utilization crosses 50%_

![](RackMultipart20230427-1-jf3tsr_html_8e29a799b7718a6a.png)

_Figure 8 Pods scaling out as Memory Utilization crosses 50%_

![](RackMultipart20230427-1-jf3tsr_html_43050f4c3ab24c91.png)

_Figure 9 Pods scaling out as Memory Utilization crosses 50%_

Finally, when the specified number of replicas are reached, the scale out stops as reflected in the snip below:

![](RackMultipart20230427-1-jf3tsr_html_5e259c03f7b9c73.png)

_Figure 10 Scale out has maxed to the number of Replicas specified in HPA_

# Conclusion

With the above step, the project requirements are completed. The underlying concept was to create a highly available infrastructure that scales out when load increases. There are obviously a great room of improvement in this set up that includes security and automation of manual tasks.

Following are few of the improvements that can be made:

1. Adding load balancer that puts the current set up behind it and in private subnet to enhances the security of ec2 instances.
2. Enhancing the Ansible part to perform left over manual tasks to fully automate.
3. Creating cron job to periodically take etcd back.
4. Storing the etcd back up to s3 bucket within AWS environment.

# Reference

1. [https://developer.hashicorp.com/terraform/intro](https://developer.hashicorp.com/terraform/intro)
2. [https://www.ansible.com/](https://www.ansible.com/)
3. [https://github.com/lkravi/kube8aws.git](https://github.com/lkravi/kube8aws.git)
4. https://github.com/lerndevops/educka.git
5. [https://github.com/inevitablewish/capstone-project.git](https://github.com/inevitablewish/capstone-project.git)

Mohsin A Malik Course end Project -1