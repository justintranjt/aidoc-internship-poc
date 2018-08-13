# Incidents Management Platform Solutions
    
When our virtual machines on Microsoft Azure and Amazon Web Services running Kubernetes containers for machine learning training crashed (and it happened often), we found errors to be difficult to trace. Even worse, it become difficult to pinpoint the solution when hundreds of metrics were taken into account at any moment. So, the solution was to take advantage of an incident management platform. I decided to choose between PagerDuty, VictorOps, and OpsGenie.

Below is some POC test code that I wrote for each of these incident management services. Along the way, I compared the feature-sets of each possible service and made a decision for our startup to prevent future failures that would go undetected.

![A look at the VictorOps interface]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/victorOps.png )*Our VM alerts from AWS clearnly appearing in VictorOps*

Having a working incident management solution that would integrate with our virtual machines performing algorithmic training on AWS (and old VMs on Azure), was essential to the efficiency and success of our machine learning platform. We were far too used to coming into work in the morning and realizing that our entire virutal machine had crashed early into the night.

With these solutions, we were able to create alerts in our cloud service of choice, integrate them to signal an incident in VictorOps (the service that I eventually chose and the one that the software engineering team took on), perform an analysis with integrataed Logz.io metrics from the ELK stack, and resolve the issue as soon as possible so that our precious server time was not wasted.

![ELK metrics in Logz.io]( https://github.com/justintranjt/justintranjt.github.io/blob/master/projects/elkz.png )*An example of logs successfully shipped from the ELK stack to Logz.io*

Note that this included writing my own integration between Microsoft Azure and VictorOps which I wrote about [here](https://justintranjt.github.io/projects/2018-07-27-victorops-azure-manual-integration/).

The guiding principles for choosing between the three incidents management solutions boiled down to two key concerns:

1. Possibility of integration with Microsofy Azure and AWS
2. Ability to view raw data and metrics created by Logz.io and from our own queries

While this project required less code than one might imagine, choosing the appropriate service to integrate into our architecture was, of course, incredibly important to maintaining a working product for our customers.
