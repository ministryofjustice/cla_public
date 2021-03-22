{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "cla-public.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cla-public.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cla-public.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "cla-public.labels" -}}
helm.sh/chart: {{ include "cla-public.chart" . }}
{{ include "cla-public.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "cla-public.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cla-public.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "cla-public.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "cla-public.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Takes our environment variables set in the values file, and arranges them
in an appropriate format
*/}}
{{- define "cla-public.app.vars" -}}
{{- $environment := .Values.environment -}}
- name: ALLOWED_HOSTS
  value: "{{ .Values.host }}"
- name:  CLA_ENV
  value: "{{ $environment }}"
{{ range $name, $data := .Values.envVars }}
- name: {{ $name }}
{{- if $data.value }}
  value: "{{ $data.value }}"
{{- else if $data.secret }}
  valueFrom:
    secretKeyRef:
      name: {{ $data.secret.name }}
      key: {{ $data.secret.key }}
      {{- if eq $environment "development" }}
      optional: true
      {{- else }}
      optional: {{ $data.secret.optional | default false }}
      {{- end }}
{{- else if $data.configmap }}
  valueFrom:
    configMapKeyReg:
      name: {{ $data.configmap.name }}
      key: {{ $data.configmap.key }}
      {{- if eq $environment "development" }}
      optional: true
      {{- else }}
      optional: {{ $data.secret.optional | default false }}
      {{- end }}
{{- end -}}
{{- end -}}
{{- end -}}
