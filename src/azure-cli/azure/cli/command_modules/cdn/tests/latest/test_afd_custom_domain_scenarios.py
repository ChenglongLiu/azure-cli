# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ResourceGroupPreparer, JMESPathCheck
from azure.cli.testsdk import ScenarioTest, record_only
from .afdx_scenario_mixin import CdnAfdScenarioMixin
from azure.mgmt.cdn.models import (AfdCertificateType, AfdMinimumTlsVersion)

class CdnAfdCustomDomainScenarioTest(CdnAfdScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer()
    def test_afd_custom_domain_crud(self, resource_group):
        profile_name = 'profiledomaintest'
        self.afd_custom_domain_list_cmd(resource_group, profile_name, expect_failure=True)

        # Create a standard Azure frontdoor profile
        self.afd_profile_create_cmd(resource_group, profile_name)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=list_checks)

        # Create a secret
        secret_name = self.create_random_name(prefix='secret', length=24)
        secret_source = "/subscriptions/d7cfdb98-c118-458d-8bdf-246be66b1f5e/resourceGroups/cdn-powershell-test/providers/Microsoft.KeyVault/vaults/cdn-powershell-test-kv/certificates/cdn-powershell-test-cer2"
        use_latest_version = True
        secret_version = None

        checks = [JMESPathCheck('provisioningState', 'Succeeded')]
        secretData = self.afd_secret_create_cmd(resource_group,
                                 profile_name,
                                 secret_name,
                                 secret_source,
                                 use_latest_version,
                                 secret_version,
                                 checks=checks).get_output_in_json()
        secretId = secretData['id']

        custom_domain_name = self.create_random_name(prefix='customdomain', length=24)
        host_name = "csharpsdk.dev.cdn.azure.cn"
        certificate_type = AfdCertificateType.customer_certificate
        minimum_tls_version = AfdMinimumTlsVersion.tls12
        azure_dns_zone = None

        checks = [JMESPathCheck('domainValidationState', 'Approved')]
        self.afd_custom_domain_create_cmd(resource_group,
                                 profile_name,
                                 custom_domain_name,
                                 host_name,
                                 certificate_type,
                                 minimum_tls_version,
                                 azure_dns_zone,
                                 secretId,
                                 checks=checks)

        show_checks = [JMESPathCheck('name', custom_domain_name),
                       JMESPathCheck('domainValidationState', 'Approved')]
        self.afd_custom_domain_show_cmd(resource_group, profile_name, custom_domain_name, checks=show_checks)

        list_checks = [JMESPathCheck('length(@)', 1),
                       JMESPathCheck('@[0].name', custom_domain_name),
                       JMESPathCheck('@[0].domainValidationState', 'Approved')]
        self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=list_checks)

        # Delete the custom domain
        self.afd_custom_domain_delete_cmd(resource_group, profile_name, custom_domain_name)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_custom_domain_list_cmd(resource_group, profile_name, checks=list_checks)
