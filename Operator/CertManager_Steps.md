## Steps to setup cert-manager operator
### Step 1: Install Operator Lifecycle Manager (OLM)

We will install OLM in your cluster. This will create a new namespace `olm` and deploy the OLM components.
[source](https://operatorhub.io/operator/cert-manager)

```bash
# Install OLM
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.32.0/install.sh | bash -s v0.32.0

# Install the operator
kubectl create -f https://operatorhub.io/install/cert-manager.yaml
```

Wait for OLM to be ready. You can check the pods in the `olm` namespace:

```bash
kubectl get pods -n olm
```

Wait for the cert-manager operator to be in `Succeeded` state
```bash
kubectl get csv -n operators -w

```

Ensure all OLM-related pods (e.g., `olm-operator`, `catalog-operator`, `package-server`) are in a `Running` state.

### Step 2: Verify the Installation and Observe Operator Components

After the Subscription is created, OLM will automatically deploy the cert-manager Operator and its associated resources.

**Check Operator Pods:**
You should see the cert-manager-operator pod (deployed by OLM) and then the actual cert-manager, cert-manager-cainjector, and cert-manager-webhook pods (deployed by the cert-manager operator itself).

```bash
kubectl get pods -n operators
```

Look for pods named something like `cert-manager-operator-...`, `cert-manager-...`, `cert-manager-cainjector-...`, and `cert-manager-webhook-...`.

**Inspect Custom Resource Definitions (CRDs):**
OLM handles the installation of CRDs. The cert-manager Operator introduces several CRDs into your cluster.

```bash
kubectl get crds | grep cert-manager
```

You should see CRDs like `certificates.cert-manager.io`, `issuers.cert-manager.io`, `clusterissuers.cert-manager.io`, and `certificaterequests.cert-manager.io`.

### Step 3: Prepare for cert-manager Operator configuration

**Create an OperatorGroup:** An OperatorGroup defines a set of namespaces that an Operator will watch. For cert-manager, we'll create an OperatorGroup in its own namespace.

```yaml
# cert-manager-operatorgroup.yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: cert-manager-operatorgroup
  namespace: operators
spec:
  targetNamespaces:
  - operators
```

Apply this manifest:
```bash
kubectl apply -f cert-manager-operatorgroup.yaml
```


**Inspect Custom Resources (CRs) (Initial State):**
At this point, you won't see any Issuer or Certificate CRs yet, as we haven't created any.

```bash
kubectl get issuer -n default
kubectl get certificate -n default
```

(You should see "No resources found" or similar, which is expected.)

### Step 4: Create an Issuer and a Certificate

Now, let's create some cert-manager Custom Resources and see the Operator in action. We'll create a simple self-signed Issuer and then a Certificate that uses it.

**Create a self-signed Issuer:**
This Issuer will be responsible for signing certificates within the default namespace.

```yaml
# selfsigned-issuer.yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: selfsigned-issuer
  namespace: default
spec:
  selfSigned: {}
```

Apply this manifest:
```bash
kubectl apply -f selfsigned-issuer.yaml
```

**Verify the Issuer is ready:**
```bash
kubectl get issuer selfsigned-issuer -n default
```

Look for STATUS to be `Ready`.

**Create a Certificate:**
This Certificate resource tells cert-manager to issue a certificate for `my-app.example.com` using our `selfsigned-issuer` and store it in a Kubernetes Secret named `my-app-tls`.

```yaml
# my-app-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-app-certificate
  namespace: default
spec:
  secretName: my-app-tls
  dnsNames:
  - my-app.example.com
  issuerRef:
    name: selfsigned-issuer
    kind: Issuer
```

Apply this manifest:
```bash
kubectl apply -f my-app-certificate.yaml
```

### Step 5: Observe Operator Reconciliation and Secret Creation

Now, let's see the cert-manager Operator in action.

**Check the Certificate status:**
The cert-manager Operator will process the Certificate resource.

```bash
kubectl get certificate my-app-certificate -n default
```

Initially, its READY status might be `False`, then change to `True` as the certificate is issued.

**Inspect the created Secret:**
Once the Certificate is ready, cert-manager will have created a TLS Secret containing the generated certificate and private key.

```bash
kubectl get secret my-app-tls -n default
```

You should see a Secret of type `kubernetes.io/tls`. You can describe it to see more details (though the actual certificate data will be base64 encoded).

```bash
kubectl describe secret my-app-tls -n default
```

**View cert-manager logs (Optional, but Recommended):**
To see the Operator's internal workings, you can view the logs of the cert-manager controller pod.

```bash
kubectl logs -f -n operators $(kubectl get pods -n operators -l app.kubernetes.io/component=controller -o jsonpath='{.items[0].metadata.name}')
```

You'll see log entries indicating that it's processing the Certificate resource, creating CertificateRequest objects, and finally creating the TLS Secret. This demonstrates the "controller" part of the Operator pattern.

**Force Operator Reconciliation by Restarting the Pod (Advanced/Troubleshooting):**
Operators continuously watch for changes in Custom Resources. However, sometimes for debugging or to force a re-evaluation, you might want to restart the operator's pod. When the cert-manager controller pod restarts, it will re-read all relevant Custom Resources and reconcile their desired state with the actual state in the cluster.

First, identify the cert-manager controller pod:
```bash
kubectl get pods -n operators -l app.kubernetes.io/component=controller
```

Then, delete the pod. Kubernetes will automatically recreate it because it's managed by a Deployment.
```bash
kubectl delete pod <cert-manager-controller-pod-name> -n operators
```

Replace `<cert-manager-controller-pod-name>` with the actual name you found in the previous command (e.g., `cert-manager-7c8d9f-abcde`).

After the new pod starts, you can again view its logs (as in step 3) to observe it re-processing existing Issuer and Certificate resources. This demonstrates the resilience and self-healing nature of Kubernetes Deployments combined with the Operator's reconciliation loop.

### Step 6: Clean Up

It's crucial to clean up your cluster after completing the assignment.

**Delete the Custom Resources:**
Always delete your custom resources before uninstalling the operator.

```bash
kubectl delete -f my-app-certificate.yaml
kubectl delete -f selfsigned-issuer.yaml
```

**Delete the cert-manager Subscription and OperatorGroup:**
```bash
kubectl delete -f cert-manager-subscription.yaml
kubectl delete -f cert-manager-operatorgroup.yaml
```

**Delete the operators namespace:**
```bash
kubectl delete namespace operators
```

**Delete the OLM namespace**
```bash
kubectl delete namespace olm
```