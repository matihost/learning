provider "google" {
  region  = var.region
  zone    = local.zone
  project = var.project
}

data "google_client_config" "current" {}
data "google_project" "current" {
}
data "google_compute_network" "default" {
  name = "default"
}

locals {
  zone     = "${var.region}-${var.zone_letter}"
  gke_name = "${var.cluster_name}-${var.env}"
  location = var.regional_cluster ? var.region : local.zone
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP Region For Deployment"
}

variable "zone_letter" {
  type        = string
  default     = "a"
  description = "GCP Region For Deployment"
}

variable "project" {
  type        = string
  description = "GCP Project For Deployment"
}

variable "cluster_name" {
  type        = string
  default     = "shared"
  description = "GKE Cluster Name Project For Deployment"
}

variable "env" {
  type        = string
  default     = "dev"
  description = "Environment"
}

variable "regional_cluster" {
  type        = bool
  default     = false
  description = "Whether to create regional cluster. Default false - which means cluster will be zonal."
}

variable "expose_master_via_external_ip" {
  type        = bool
  default     = false
  description = "Whether to expose Kube API as ExternalIP. Default false - which means cluster will be available only from internal VPC"
}

variable "external_access_ip" {
  type        = string
  description = "The public IP which is allowed to access Kube API"
}

variable "external_dns_k8s_namespace" {
  type        = string
  default     = "external-dns"
  description = "GKE Namespace where ExternalDNS is being deployed"
}

variable "external_dns_k8s_sa_name" {
  type        = string
  default     = "external-dns"
  description = "ExternalDNS  K8S ServiceAccount"
}
