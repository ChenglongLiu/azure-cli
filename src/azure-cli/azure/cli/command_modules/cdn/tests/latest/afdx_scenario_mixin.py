# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from .scenario_mixin import add_tags

def _add_paramter_if_needed(command, paramter_name, parameter_value):
    if parameter_value is not None:
        return f'{command} --{paramter_name} {parameter_value}'
    else:
        return command

# pylint: disable=too-many-public-methods
class CdnAfdScenarioMixin:
    def afd_profile_create_cmd(self, resource_group_name, profile_name, tags=None, checks=None, options=None, sku=None):
        command = f'cdn profile create -g {resource_group_name} -n {profile_name} --sku Standard_AzureFrontDoor'
        if tags:
            command = command + ' --tags {}'.format(tags)
        if options:
            command = command + ' ' + options

        return self.cmd(command, checks)

    def afd_endpoint_create_cmd(self, resource_group_name, profile_name, endpoint_name, origin_response_timeout_seconds, enabled_state,
                    location=None, tags=None, no_wait=None, checks=None):
        cmd = f'cdn afd-endpoint create -g {resource_group_name} --endpoint-name {endpoint_name} --profile-name {profile_name} --origin-response-timeout-seconds {origin_response_timeout_seconds} --enabled-state {enabled_state}'

        if tags:
            cmd = add_tags(cmd, tags)

        return self.cmd(cmd, checks)

    def afd_endpoint_update_cmd(self, resource_group_name, profile_name, endpoint_name, origin_response_timeout_seconds=None, enabled_state=None, tags=None, checks=None, options=None):
        command = f'cdn afd-endpoint update -g {resource_group_name} --endpoint-name {endpoint_name} --profile-name {profile_name}'
        if tags:
            command = add_tags(command, tags)

        command =  _add_paramter_if_needed(command, "origin-response-timeout-seconds", origin_response_timeout_seconds)
        command =  _add_paramter_if_needed(command, "enabled-state", enabled_state)

        if options:
            command = command + ' ' + options

        return self.cmd(command, checks)

    def afd_endpoint_show_cmd(self, resource_group_name, profile_name, endpoint_name, checks=None, options=None):
        command = 'cdn afd-endpoint show -g {resource_group_name} --endpoint-name {endpoint_name} --profile-name {profile_name}'
        if options:
            command = command + ' ' + options
        return self.cmd(command, checks)

    def afd_endpoint_purge_cmd(self, resource_group_name, endpoint_name, profile_name, content_paths, checks=None):
        command = f'cdn afd-endpoint purge -g {resource_group_name} --endpoint-name {endpoint_name} --profile-name {profile_name} --content-paths {" ".join(content_paths)}'
        return self.cmd(command, checks)

    def afd_rule_set_add_cmd(self, resource_group_name, rule_set_name, profile_name, checks=None):
        command = f'az cdn afd-rule-set create -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name}'

        return self.cmd(command, checks)

    def afd_rule_set_delete_cmd(self, resource_group_name, rule_set_name, profile_name, checks=None):
        command = f'az cdn afd-rule-set delete -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --yes'

        return self.cmd(command, checks)

    def afd_rule_set_list_cmd(self, resource_group_name, profile_name, checks=None, expect_failure=False):
        command = f'az cdn afd-rule-set list -g {resource_group_name} --profile-name {profile_name}'

        return self.cmd(command, checks, expect_failure=expect_failure)

    def afd_rule_set_show_cmd(self, resource_group_name, rule_set_name, profile_name, checks=None, expect_failure=False):
        command = f'az cdn afd-rule-set show -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name}'

        return self.cmd(command, checks, expect_failure=expect_failure)

    def afd_rule_list_cmd(self, resource_group_name, rule_set_name,  profile_name, checks=None, expect_failure=False):
        command = f'az cdn afd-rule list -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name}'

        return self.cmd(command, checks, expect_failure=expect_failure)

    def afd_rule_show_cmd(self, resource_group_name, rule_set_name, rule_name, profile_name, checks=None):
        command = f'az cdn afd-rule show -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --rule-name {rule_set_name}'

        return self.cmd(command, checks)

    def afd_rule_add_cmd(self, resource_group_name, rule_set_name, rule_name, profile_name, options=None, checks=None):
        command = f'az cdn afd-rule create -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --rule-name {rule_name}'

        if options:
            command = command + ' ' + options

        return self.cmd(command, checks)

    def afd_rule_add_condition_cmd(self, resource_group_name, rule_set_name, rule_name, profile_name, checks=None, options=None):
        command = f'cdn afd-rule condition add -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --rule-name {rule_name}'
        if options:
            command = command + ' ' + options
        return self.cmd(command, checks)

    def afd_rule_add_action_cmd(self, resource_group_name, rule_set_name, rule_name, profile_name, checks=None, options=None):
        command = f'cdn afd-rule action add -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --rule-name {rule_name}'
        if options:
            command = command + ' ' + options
        return self.cmd(command, checks)

    def afd_rule_delete_cmd(self, resource_group_name, rule_set_name, rule_name, profile_name, checks=None, options=None):
        command = f'cdn afd-rule delete -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --rule-name {rule_name} --yes'
        if options:
            command = command + ' ' + options
        return self.cmd(command, checks)

    def afd_rule_remove_condition_cmd(self, resource_group_name, rule_set_name, rule_name, profile_name, index, checks=None, options=None):
        command = f'cdn afd-rule condition remove -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --rule-name {rule_name} --index {index}'
        if options:
            command = command + ' ' + options
        return self.cmd(command, checks)

    def afd_rule_remove_action_cmd(self, resource_group_name, rule_set_name, rule_name, profile_name, index, checks=None, options=None):
        command = f'cdn afd-rule action remove -g {resource_group_name} --rule-set-name {rule_set_name} --profile-name {profile_name} --rule-name {rule_name} --index {index}'
        if options:
            command = command + ' ' + options
        return self.cmd(command, checks)

    def afd_endpoint_list_cmd(self, resource_group_name, profile_name, checks=None, expect_failure=False):
        command = f'cdn afd-endpoint list -g {resource_group_name} --profile-name {profile_name}'
        return self.cmd(command, checks, expect_failure=expect_failure)

    def afd_endpoint_delete_cmd(self, resource_group_name, endpoint_name, profile_name, checks=None):
        command = f'cdn afd-endpoint delete -g {resource_group_name} --endpoint-name {endpoint_name} --profile-name {profile_name}'
        return self.cmd(command, checks)

    def afd_secret_create_cmd(self, resource_group_name, profile_name, secret_name, secret_source, use_latest_version=True, secret_version=None, checks=None):
        cmd = f'cdn afd-secret create -g {resource_group_name} --profile-name {profile_name} --secret-name {secret_name} --secret-source {secret_source} --use-latest-version {use_latest_version}'

        if secret_version:
            cmd += f' --secret-version={secret_version}'

        return self.cmd(cmd, checks)

    def afd_secret_list_cmd(self, resource_group_name, profile_name, checks=None, expect_failure=False):
        command = f'cdn afd-secret list -g {resource_group_name} --profile-name {profile_name}'
        return self.cmd(command, checks, expect_failure=expect_failure)

    def afd_secret_show_cmd(self, resource_group_name, profile_name, secret_name, checks=None):
        command = f'cdn afd-secret show -g {resource_group_name} --profile-name {profile_name} --secret-name {secret_name}'
        return self.cmd(command, checks)

    def afd_secret_delete_cmd(self, resource_group_name, profile_name, secret_name, checks=None):
        command = f'cdn afd-secret delete -g {resource_group_name} --profile-name {profile_name} --secret-name {secret_name} --yes'
        return self.cmd(command, checks)
        
    def afd_custom_domain_create_cmd(self, resource_group_name, profile_name, custom_domain_name, host_name, certificate_type, minimum_tls_version, azure_dns_zone=None, secret=None, checks=None):
        cmd = f'cdn afd-custom-domain create -g {resource_group_name} --profile-name {profile_name} --custom-domain-name {custom_domain_name} --host-name {host_name} --certificate-type {certificate_type} --minimum-tls-version {minimum_tls_version}'

        if azure_dns_zone:
            cmd += f' --azure-dns-zone={azure_dns_zone}'
        if secret:
            cmd += f' --secret={secret}'

        return self.cmd(cmd, checks)

    def afd_custom_domain_list_cmd(self, resource_group_name, profile_name, checks=None, expect_failure=False):
        command = f'cdn afd-custom-domain list -g {resource_group_name} --profile-name {profile_name}'
        return self.cmd(command, checks, expect_failure=expect_failure)

    def afd_custom_domain_show_cmd(self, resource_group_name, profile_name, custom_domain_name, checks=None):
        command = f'cdn afd-custom-domain show -g {resource_group_name} --profile-name {profile_name} --custom-domain-name {custom_domain_name} '
        return self.cmd(command, checks)

    def afd_custom_domain_delete_cmd(self, resource_group_name, profile_name, custom_domain_name, checks=None):
        command = f'cdn afd-custom-domain delete -g {resource_group_name} --profile-name {profile_name} --custom-domain-name {custom_domain_name} --yes'
        return self.cmd(command, checks)

    def afd_security_policy_create_cmd(self, resource_group_name, profile_name, security_policy_name, domain_ids, waf_policy_id, checks=None):
        cmd = f'cdn afd-security-policy create -g {resource_group_name} --profile-name {profile_name} --security-policy-name {security_policy_name} --waf-policy-id {waf_policy_id}'
        if domain_ids:
            cmd += " --domain-ids " + " ".join(["'{}'".format(domain_id) for domain_id in domain_ids])

        return self.cmd(cmd, checks)

    def afd_security_policy_update_cmd(self, resource_group_name, profile_name, security_policy_name, domain_ids, waf_policy_id, checks=None):
        cmd = f'cdn afd-security-policy update -g {resource_group_name} --profile-name {profile_name} --security-policy-name {security_policy_name} --waf-policy-id {waf_policy_id}'
        if domain_ids:
            cmd += " --domain-ids " + " ".join(["'{}'".format(domain_id) for domain_id in domain_ids])

        return self.cmd(cmd, checks)

    def afd_security_policy_list_cmd(self, resource_group_name, profile_name, checks=None, expect_failure=False):
        command = f'cdn afd-security-policy list -g {resource_group_name} --profile-name {profile_name}'
        return self.cmd(command, checks, expect_failure=expect_failure)

    def afd_security_policy_show_cmd(self, resource_group_name, profile_name, security_policy_name, checks=None):
        command = f'cdn afd-security-policy show -g {resource_group_name} --profile-name {profile_name} --security-policy-name {security_policy_name}'
        return self.cmd(command, checks)

    def afd_security_policy_delete_cmd(self, resource_group_name, profile_name, security_policy_name, checks=None):
        command = f'cdn afd-security-policy delete -g {resource_group_name} --profile-name {profile_name} --security-policy-name {security_policy_name} --yes'
        return self.cmd(command, checks)
