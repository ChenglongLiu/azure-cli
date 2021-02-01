# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ResourceGroupPreparer, JMESPathCheck
from azure.cli.testsdk import ScenarioTest, record_only
from .afdx_scenario_mixin import CdnAfdScenarioMixin

class CdnAfdSecurityPolicyScenarioTest(CdnAfdScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer()
    def test_afd_secret_crud(self, resource_group):
        profile_name = 'profilesecuritytest'
        self.afd_security_policy_list_cmd(resource_group, profile_name, expect_failure=True)

        # List get empty
        self.afd_profile_create_cmd(resource_group, profile_name)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_security_policy_list_cmd(resource_group, profile_name, checks=list_checks)

        # Create an endpoint
        endpoint1_name = self.create_random_name(prefix='endpoint1', length=24)
        endpoint2_name = self.create_random_name(prefix='endpoint2', length=24)
        origin_response_timeout_seconds = 100
        enabled_state = "Enabled"
        endpoint_checks = [JMESPathCheck('originResponseTimeoutSeconds', 100),
                           JMESPathCheck('enabledState', 'Enabled')]
        endpoint1 = self.afd_endpoint_create_cmd(resource_group,
                                 profile_name,
                                 endpoint1_name,
                                 origin_response_timeout_seconds,
                                 enabled_state,
                                 checks=endpoint_checks).get_output_in_json()
        endpoint2 = self.afd_endpoint_create_cmd(resource_group,
                                 profile_name,
                                 endpoint2_name,
                                 origin_response_timeout_seconds,
                                 enabled_state,
                                 checks=endpoint_checks).get_output_in_json()

        # Create a security policy
        security_policy_name = self.create_random_name(prefix='security', length=24)
        domain_ids = list()
        domain_ids.append(endpoint1['id'])
        domain_ids.append(endpoint2['id'])
        waf_policy_id = '/subscriptions/d7cfdb98-c118-458d-8bdf-246be66b1f5e/resourcegroups/chengll-test3632/providers/Microsoft.Network/frontdoorwebapplicationfirewallpolicies/hellowaf'

        checks = [JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_security_policy_create_cmd(resource_group,
                                 profile_name,
                                 security_policy_name,
                                 domain_ids,
                                 waf_policy_id,
                                 checks=checks)

        show_checks = [JMESPathCheck('name', security_policy_name),
                       JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_security_policy_show_cmd(resource_group, profile_name, security_policy_name, checks=show_checks)

        list_checks = [JMESPathCheck('length(@)', 1),
                       JMESPathCheck('@[0].name', security_policy_name),
                       JMESPathCheck('@[0].provisioningState', 'Succeeded')]
        self.afd_security_policy_list_cmd(resource_group, profile_name, checks=list_checks)

        """ Update is not ready
        # Update the security policy
        domain_ids = list()
        domain_ids.append(endpoint1['id'])
        checks = [JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_security_policy_update_cmd(resource_group,
                                 profile_name,
                                 security_policy_name,
                                 domain_ids,
                                 waf_policy_id,
                                 checks=checks)
        """

        # Delete the security policy
        self.afd_security_policy_delete_cmd(resource_group, profile_name, security_policy_name)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_security_policy_list_cmd(resource_group, profile_name, checks=list_checks)