# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from typing import (Optional, List)


from azure.mgmt.cdn.models import (AFDEndpoint, HealthProbeRequestType, EnabledState, Route, LinkToDefaultDomain, ResourceReference,
                                   AFDEndpointProtocols, HttpsRedirect, ForwardingProtocol, QueryStringCachingBehavior, RouteUpdateParameters, HealthProbeParameters,
                                   AFDOrigin, AFDOriginGroup, SharedPrivateLinkResourceProperties, CompressionSettings, LoadBalancingSettingsParameters,
                                   SecurityPolicyWebApplicationFirewallParameters, SecurityPolicyWebApplicationFirewallAssociation,
                                   CustomerCertificateParameters, AFDDomain, AFDDomainHttpsParameters, AfdCertificateType, AfdMinimumTlsVersion,
                                   AFDEndpointUpdateParameters, MatchProcessingBehavior)

from azure.mgmt.cdn.operations import (OriginsOperations, AFDOriginGroupsOperations, AFDOriginsOperations, SecretsOperations, AFDEndpointsOperations,
                                       RoutesOperations, RuleSetsOperations, RulesOperations, SecurityPoliciesOperations, AFDCustomDomainsOperations)

from azure.cli.core.util import (sdk_no_wait)
from knack.util import CLIError
from knack.log import get_logger
from .custom import _update_mapper

logger = get_logger(__name__)

def create_afd_endpoint(client, resource_group_name, profile_name, endpoint_name, origin_response_timeout_seconds, enabled_state,
                    location=None, tags=None, no_wait=None):

    endpoint = AFDEndpoint(location=location,
                        origin_response_timeout_seconds = origin_response_timeout_seconds,
                        enabled_state = enabled_state,
                        tags=tags)

    return sdk_no_wait(no_wait, client.afd_endpoints.create, resource_group_name, profile_name, endpoint_name, endpoint)

def update_afd_endpoint(client:AFDEndpointsOperations, resource_group_name, profile_name, endpoint_name, origin_response_timeout_seconds=None, enabled_state=None, tags=None):
    update_properties = AFDEndpointUpdateParameters(
        origin_response_timeout_seconds=origin_response_timeout_seconds,
        enabled_state=enabled_state,
        tags=tags
    )
     
    return client.update(resource_group_name, profile_name, endpoint_name, update_properties)

def create_afd_origin_group(client: AFDOriginGroupsOperations,
                        resource_group_name: str,
                        profile_name: str,
                        origin_group_name: str,
                        load_balancing_sample_size: int,
                        load_balancing_successful_samples_required: int,
                        load_balancing_additional_latency_in_milliseconds: int,
                        probe_request_type: HealthProbeRequestType,
                        probe_protocol: str,
                        probe_path: str,
                        probe_interval_in_seconds: int = 240):

    # Move these to the parameters list once support is added in RP:
    response_error_detection_error_types: Optional[str] = None
    response_error_detection_failover_threshold: Optional[int] = None
    response_error_detection_status_code_ranges: Optional[str] = None

    health_probe_parameters = HealthProbeParameters(probe_path=probe_path,
                                                  probe_request_type=probe_request_type,
                                                  probe_protocol=probe_protocol,
                                                  probe_interval_in_seconds=probe_interval_in_seconds)

    load_balancing_settings_parameters = LoadBalancingSettingsParameters(sample_size=load_balancing_sample_size,
                                                  successful_samples_required=load_balancing_successful_samples_required,
                                                  additional_latency_in_milliseconds=load_balancing_additional_latency_in_milliseconds)

    afd_origin_group = AFDOriginGroup(load_balancing_settings=load_balancing_settings_parameters,
                               health_probe_settings=health_probe_parameters)

    return client.create(resource_group_name,
                         profile_name,
                         origin_group_name,
                         afd_origin_group).result()

def update_afd_origin_group(client: AFDOriginGroupsOperations,
                        resource_group_name: str,
                        profile_name: str,
                        origin_group_name: str,
                        load_balancing_sample_size: int = None,
                        load_balancing_successful_samples_required: int = None,
                        load_balancing_additional_latency_in_milliseconds: int = None,
                        probe_request_type: HealthProbeRequestType = None,
                        probe_protocol: str = None,
                        probe_path: str = None,
                        probe_interval_in_seconds: int = 240):

    # Move these to the parameters list once support is added in RP:
    response_error_detection_error_types: Optional[str] = None
    response_error_detection_failover_threshold: Optional[int] = None
    response_error_detection_status_code_ranges: Optional[str] = None

    existing = client.get(resource_group_name, profile_name, origin_group_name)
    health_probe_parameters = HealthProbeParameters(probe_path=probe_path if probe_path is not None else existing.health_probe_settings.probe_path,
                                                  probe_request_type=probe_request_type if probe_request_type is not None else existing.health_probe_settings.probe_request_type,
                                                  probe_protocol=probe_protocol if probe_protocol is not None else existing.health_probe_settings.probe_protocol,
                                                  probe_interval_in_seconds=probe_interval_in_seconds if probe_interval_in_seconds is not None else existing.health_probe_settings.probe_interval_in_seconds)

    load_balancing_settings_parameters = LoadBalancingSettingsParameters(sample_size=load_balancing_sample_size if load_balancing_sample_size is not None else existing.load_balancing_settings.sample_size,
                                                  successful_samples_required=load_balancing_successful_samples_required if load_balancing_successful_samples_required is not None else existing.load_balancing_settings.successful_samples_required,
                                                  additional_latency_in_milliseconds=load_balancing_additional_latency_in_milliseconds if load_balancing_additional_latency_in_milliseconds is not None else existing.load_balancing_settings.additional_latency_in_milliseconds)

    afd_origin_group = AFDOriginGroup(load_balancing_settings=load_balancing_settings_parameters,
                               health_probe_settings=health_probe_parameters)

    return client.create(resource_group_name,
                         profile_name,
                         origin_group_name,
                         afd_origin_group).result()


def create_afd_origin(client: AFDOriginsOperations,
                  resource_group_name: str,
                  profile_name: str,
                  origin_group_name: str,
                  origin_name: str,
                  host_name: str,
                  enabled_state: EnabledState,
                  enable_private_link: bool = None,
                  private_link: str = None,
                  private_link_location: str = None,
                  group_id: str = None,
                  request_message: str = None,
                  http_port: int = 80,
                  https_port: int = 443,
                  origin_host_header: Optional[str] = None,
                  priority: int = 1,
                  weight: int = 1000):

    from azure.mgmt.cdn.models import ResourceReference

    shared_private_link_resource = None
    if enable_private_link:
        shared_private_link_resource =  SharedPrivateLinkResourceProperties(
                                            private_link=ResourceReference(id=private_link),
                                            private_link_location=private_link_location,
                                            group_id=group_id,
                                            request_message=request_message
                                        )

    return client.create(resource_group_name,
                         profile_name,
                         origin_group_name,
                         origin_name,
                         AFDOrigin(
                             host_name=host_name,
                             http_port=http_port,
                             https_port=https_port,
                             origin_host_header=origin_host_header,
                             priority=priority,
                             weight=weight,
                             shared_private_link_resource=shared_private_link_resource,
                             enabled_state=enabled_state))

def update_afd_origin(client: AFDOriginsOperations,
                  resource_group_name: str,
                  profile_name: str,
                  origin_group_name: str,
                  origin_name: str,
                  host_name: str = None,
                  enabled_state: EnabledState = None,
                  http_port: int = None,
                  https_port: int = None,
                  origin_host_header: Optional[str] = None,
                  priority: int = None,
                  weight: int = None,
                  enable_private_link: bool = None,
                  private_link: str = None,
                  private_link_location: str = None,
                  group_id: str = None,
                  request_message: str = None):

    existing = client.get(resource_group_name, profile_name, origin_group_name, origin_name)
    shared_private_link_resource = existing.shared_private_link_resource
    if enable_private_link is not None:
        if enable_private_link:
            if shared_private_link_resource is None:                
                shared_private_link_resource =  SharedPrivateLinkResourceProperties(
                                                    private_link=ResourceReference(id=private_link),
                                                    private_link_location=private_link_location,
                                                    group_id=group_id,
                                                    request_message=request_message
                                                )
            else:
                shared_private_link_resource =  SharedPrivateLinkResourceProperties(
                                    private_link=ResourceReference(id=private_link if private_link is not None else shared_private_link_resource.private_link),
                                    private_link_location=private_link_location if private_link_location is not None else shared_private_link_resource.private_link_location,
                                    group_id=group_id if group_id is not None else shared_private_link_resource.group_id,
                                    request_message=request_message if request_message is not None else shared_private_link_resource.request_message
                                )
        else:
            shared_private_link_resource = None

    # client.update does not allow unset field
    return client.create(resource_group_name,
                         profile_name,
                         origin_group_name,
                         origin_name,
                         AFDOrigin(
                             host_name=host_name if host_name is not None else existing.host_name,
                             http_port=http_port if http_port is not None else existing.http_port,
                             https_port=https_port if https_port is not None else existing.https_port,
                             origin_host_header=origin_host_header if origin_host_header is not None else existing.origin_host_header,
                             priority=priority if priority is not None else existing.priority,
                             weight=weight if weight is not None else existing.priority,
                             shared_private_link_resource=shared_private_link_resource,
                             enabled_state=enabled_state))


def create_afd_route(client: RoutesOperations,
                  resource_group_name: str,
                  profile_name: str,
                  endpoint_name: str,
                  route_name: str,
                  https_redirect: HttpsRedirect,
                  supported_protocols: List[AFDEndpointProtocols],
                  origin_group: str,
                  forwarding_protocol: ForwardingProtocol,                  
                  link_to_default_domain: LinkToDefaultDomain,
                  is_compression_enabled: bool=False,
                  content_types_to_compress: List[str] = None,
                  query_string_caching_behavior: QueryStringCachingBehavior = None,
                  custom_domains: List[str] = None,
                  origin_path: Optional[str] = None,
                  patterns_to_match: List[str] = ['/*'],
                  rule_sets: List[str] = None):

    from azure.mgmt.cdn.models import ResourceReference
   
    formatted_custom_domains = []
    if custom_domains is not None:
        for custom_domain in custom_domains:
            if '/' not in custom_domain:
                    custom_domain = f'/subscriptions/{client.config.subscription_id}/resourceGroups/{resource_group_name}' \
                            f'/providers/Microsoft.Cdn/profiles/{profile_name}/customDomains/{custom_domain}'
            
            # If the origin is not an ID, assume it's a name and format it as an ID.
            formatted_custom_domains.append(ResourceReference(id=custom_domain))
    
    if '/' not in origin_group:
            origin_group = f'/subscriptions/{client.config.subscription_id}/resourceGroups/{resource_group_name}' \
                            f'/providers/Microsoft.Cdn/profiles/{profile_name}/originGroups/{origin_group}'

    from azure.mgmt.cdn.models import CompressionSettings
    compression_settings = CompressionSettings(
        content_types_to_compress=content_types_to_compress,
        is_compression_enabled=is_compression_enabled
    )

    formatted_rule_sets = []
    if rule_sets is not None:        
        for rule_set in rule_sets:
            if '/' not in rule_set:
                    rule_set = f'/subscriptions/{client.config.subscription_id}/resourceGroups/{resource_group_name}' \
                            f'/providers/Microsoft.Cdn/profiles/{profile_name}/ruleSets/{rule_set}'
            
            formatted_rule_sets.append(ResourceReference(id=rule_set))

    return client.create(resource_group_name,
                         profile_name,
                         endpoint_name,
                         route_name,
                         Route(
                             custom_domains=formatted_custom_domains,
                             origin_path = origin_path,
                             patterns_to_match=patterns_to_match,
                             supported_protocols=supported_protocols,
                             https_redirect=https_redirect,
                             origin_group=ResourceReference(id=origin_group),
                             forwarding_protocol=forwarding_protocol,
                             rule_sets=formatted_rule_sets,
                             query_string_caching_behavior=query_string_caching_behavior,
                             compression_settings=compression_settings,
                             link_to_default_domain=link_to_default_domain))

def update_afd_route(client: RoutesOperations,
                  resource_group_name: str,
                  profile_name: str,
                  endpoint_name: str,
                  route_name: str,
                  https_redirect: HttpsRedirect = None,
                  supported_protocols: List[AFDEndpointProtocols] = None,
                  origin_group: str = None,
                  forwarding_protocol: ForwardingProtocol = None,                  
                  link_to_default_domain: LinkToDefaultDomain = None,
                  is_compression_enabled: bool=False,
                  content_types_to_compress: List[str] = None,
                  query_string_caching_behavior: QueryStringCachingBehavior = None,
                  custom_domains: List[str] = None,
                  origin_path: Optional[str] = None,
                  patterns_to_match: List[str] = None,
                  rule_sets: List[str] = None):

    existing = client.get(resource_group_name,
                      profile_name,
                      endpoint_name,
                      route_name)

    route = Route(
                custom_domains=existing.custom_domains,
                origin_path = existing.origin_path if origin_path is None else origin_path,
                patterns_to_match=existing.patterns_to_match if patterns_to_match is None else patterns_to_match,
                supported_protocols=existing.supported_protocols if supported_protocols is None else supported_protocols,
                https_redirect=existing.https_redirect if https_redirect is None else https_redirect,
                origin_group=existing.origin_group,
                forwarding_protocol=existing.forwarding_protocol if forwarding_protocol is None else forwarding_protocol,
                rule_sets=existing.rule_sets,
                query_string_caching_behavior=existing.query_string_caching_behavior if query_string_caching_behavior is None else query_string_caching_behavior,
                compression_settings=existing.compression_settings,
                link_to_default_domain=existing.link_to_default_domain if link_to_default_domain is None else link_to_default_domain)    
    
    if custom_domains is not None:
        formatted_custom_domains = []
        for custom_domain in custom_domains:
            if '/' not in custom_domain:
                    custom_domain = f'/subscriptions/{client.config.subscription_id}/resourceGroups/{resource_group_name}' \
                            f'/providers/Microsoft.Cdn/profiles/{profile_name}/customDomains/{custom_domain}'
            
            # If the origin is not an ID, assume it's a name and format it as an ID.
            formatted_custom_domains.append(ResourceReference(id=custom_domain))

        route.custom_domains = formatted_custom_domains
    
    if origin_group is not None:
        if '/' not in origin_group:
                origin_group = f'/subscriptions/{client.config.subscription_id}/resourceGroups/{resource_group_name}' \
                                f'/providers/Microsoft.Cdn/profiles/{profile_name}/originGroups/{origin_group}'

        route.origin_group = origin_group

    if rule_sets is not None:
        formatted_rule_sets = []
        for rule_set in rule_sets:
            if '/' not in rule_set:
                    rule_set = f'/subscriptions/{client.config.subscription_id}/resourceGroups/{resource_group_name}' \
                            f'/providers/Microsoft.Cdn/profiles/{profile_name}/ruleSets/{rule_set}'
            
            # If the origin is not an ID, assume it's a name and format it as an ID.
            formatted_rule_sets.append(ResourceReference(id=rule_set))

        route.rule_sets = formatted_rule_sets
    
    if is_compression_enabled is not None:
        if is_compression_enabled:
            if route.compression_settings is None:
                route.compression_settings = CompressionSettings(
                    content_types_to_compress=content_types_to_compress,
                    is_compression_enabled=is_compression_enabled
                )
            else:
                route.compression_settings = CompressionSettings(
                    content_types_to_compress=content_types_to_compress if content_types_to_compress is not None else route.compression_settings.content_types_to_compress,
                    is_compression_enabled=is_compression_enabled
                )
        else:
            route.compression_settings = None

    return client.create(resource_group_name,
                         profile_name,
                         endpoint_name,
                         route_name,
                         route)

def create_afd_rule_set(cmd,
                  resource_group_name: str,
                  profile_name: str,
                  rule_set_name: str):

    from .._client_factory import cf_cdn
    client = cf_cdn(cmd.cli_ctx).rule_sets

    # The existing version of autorest.python does not support empty body for PUT request
    # Use send_raw_request as an work-around.
    # We should switch to native SDK call once autorest.python has fixed that.
    from azure.mgmt.cdn.models import RuleSet, AfdErrorResponseException
    from azure.cli.core.util import send_raw_request
    from msrestazure.polling.arm_polling import ARMPolling
    from msrest.polling import LROPoller
    from msrest.pipeline import ClientRawResponse    

    url = _build_rule_set_put_url(client.config.subscription_id,
                                  resource_group_name,
                                  profile_name,
                                  rule_set_name,
                                  client.api_version)

    response = send_raw_request(cmd.cli_ctx, 'put', url, body=None)
    if response.status_code not in [200, 201, 202]:
        raise AfdErrorResponseException(client._deserialize, response)

    deserialized = client._deserialize('RuleSet', response)
    client_raw_response = ClientRawResponse(deserialized, response)

    def get_long_running_output(response):
        deserialized = client._deserialize('RuleSet', response)
        return deserialized
     
    polling_method = ARMPolling(client.config.long_running_operation_timeout)
    return LROPoller(client._client, client_raw_response, get_long_running_output, polling_method)

# pylint: disable=too-many-locals
def create_afd_rule(client: RulesOperations, resource_group_name, profile_name, rule_set_name,
             order, rule_name, action_name, match_variable=None, operator=None,
             match_values=None, selector=None, negate_condition=None, transform=None,
             cache_behavior=None, cache_duration=None, header_action=None,
             header_name=None, header_value=None, query_string_behavior=None, query_parameters=None,
             redirect_type=None, redirect_protocol=None, custom_hostname=None, custom_path=None,
             custom_querystring=None, custom_fragment=None, source_pattern=None,
             destination=None, preserve_unmatched_path=None, match_processing_behavior : MatchProcessingBehavior = None):
    from azure.mgmt.cdn.models import Rule
    from .custom import create_condition
    from .custom import create_action

    conditions = []
    condition = create_condition(match_variable, operator, match_values, selector, negate_condition, transform)
    if condition is not None:
        conditions.append(condition)
    
    actions = []
    action = create_action(action_name, cache_behavior, cache_duration, header_action, header_name,
                           header_value, query_string_behavior, query_parameters, redirect_type,
                           redirect_protocol, custom_hostname, custom_path, custom_querystring,
                           custom_fragment, source_pattern, destination, preserve_unmatched_path)
    if action is not None:
        actions.append(action)

    rule = Rule(
        name=rule_name,
        order=order,
        conditions=conditions,
        actions=actions,
        match_processing_behavior = match_processing_behavior
    )

    return client.create(resource_group_name,
                         profile_name,
                         rule_set_name,
                         rule_name,
                         rule=rule)

def add_afd_rule_condition(client: RulesOperations, resource_group_name, profile_name, rule_set_name,
                  rule_name, match_variable, operator, match_values=None, selector=None,
                  negate_condition=None, transform=None):
    from .custom import create_condition

    existing_rule = client.get(resource_group_name, profile_name, rule_set_name, rule_name)
    condition = create_condition(match_variable, operator, match_values, selector, negate_condition, transform)
    existing_rule.conditions.append(condition)

    return client.create(resource_group_name,
                         profile_name,
                         rule_set_name,
                         rule_name,
                         rule=existing_rule)

def add_afd_rule_action(client: RulesOperations, resource_group_name, profile_name, rule_set_name,
               rule_name, action_name, cache_behavior=None, cache_duration=None,
               header_action=None, header_name=None, header_value=None, query_string_behavior=None,
               query_parameters=None, redirect_type=None, redirect_protocol=None, custom_hostname=None,
               custom_path=None, custom_querystring=None, custom_fragment=None, source_pattern=None,
               destination=None, preserve_unmatched_path=None):
    from .custom import create_action

    existing_rule = client.get(resource_group_name, profile_name, rule_set_name, rule_name)
    action = create_action(action_name, cache_behavior, cache_duration, header_action, header_name,
                           header_value, query_string_behavior, query_parameters, redirect_type,
                           redirect_protocol, custom_hostname, custom_path, custom_querystring,
                           custom_fragment, source_pattern, destination, preserve_unmatched_path)

    existing_rule.actions.append(action)
    return client.create(resource_group_name,
                         profile_name,
                         rule_set_name,
                         rule_name,
                         rule=existing_rule)

def remove_afd_rule_condition(client: RulesOperations, resource_group_name, profile_name, rule_set_name, rule_name, index):
    existing_rule = client.get(resource_group_name, profile_name, rule_set_name, rule_name) 
    if len(existing_rule.conditions) > 1 and index < len(existing_rule.conditions):
        existing_rule.conditions.pop(index)
    else:
        logger.warning("Invalid condition index found. This command will be skipped. Please check the rule.")

    return client.create(resource_group_name,
                         profile_name,
                         rule_set_name,
                         rule_name,
                         rule=existing_rule)

def remove_afd_rule_action(client: RulesOperations, resource_group_name, profile_name, rule_set_name, rule_name, index):
    existing_rule = client.get(resource_group_name, profile_name, rule_set_name, rule_name) 
    if len(existing_rule.actions) > 1 and index < len(existing_rule.actions):
        existing_rule.actions.pop(index)
    else:
        logger.warning("Invalid condition index found. This command will be skipped. Please check the rule.")

    return client.create(resource_group_name,
                         profile_name,
                         rule_set_name,
                         rule_name,
                         rule=existing_rule)

def create_afd_security_policy(client: SecurityPoliciesOperations, 
                                resource_group_name, 
                                profile_name, 
                                security_policy_name,                                
                                domain_ids: List[str],
                                waf_policy_id: str):

    if any([("/afdEndpoints/" not in domain_id and "/customdomains/" not in domain_id) for domain_id in domain_ids]):
        raise CLIError('Domain id should either be endpoint id or custom domain id.')

    if "/frontdoorwebapplicationfirewallpolicies/" not in waf_policy_id:
        raise CLIError('waf_policy_id should be front door web application firewall policy id.')

    # Add patterns and multiple domains support in the feature
    parameters = SecurityPolicyWebApplicationFirewallParameters(
        waf_policy=ResourceReference(id=waf_policy_id),
        associations=[SecurityPolicyWebApplicationFirewallAssociation(domains=[ResourceReference(id=doamin_id) for doamin_id in domain_ids], patterns_to_match=["/*"])]
    )

    return client.create(resource_group_name,
                         profile_name,
                         security_policy_name,
                         parameters=parameters)

def update_afd_security_policy(client: SecurityPoliciesOperations, 
                                resource_group_name, 
                                profile_name, 
                                security_policy_name,                                
                                domain_ids: List[str] = None,
                                waf_policy_id: str = None):    
    
    if domain_ids is not None and any([("/afdEndpoints/" not in domain_id and "/customdomains/" not in domain_id) for domain_id in domain_ids]):
        raise CLIError('Domain id should either be endpoint id or custom domain id.')

    if waf_policy_id is not None and "/frontdoorwebapplicationfirewallpolicies/" not in waf_policy_id:
        raise CLIError('waf_policy_id should be front door web application firewall policy id.')
    
    existing = client.get(resource_group_name, profile_name, security_policy_name)

    # Add patterns and multiple domains support in the feature
    parameters = SecurityPolicyWebApplicationFirewallParameters(
        waf_policy=ResourceReference(id=waf_policy_id) if waf_policy_id is not None else existing.parameters.waf_policy,
        associations=[SecurityPolicyWebApplicationFirewallAssociation(domains=[ResourceReference(id=doamin_id) for doamin_id in domain_ids], 
                    patterns_to_match=["/*"])] if domain_ids is not None else existing.parameters.associations
    )

    # patch, no update
    return client.patch(resource_group_name,
                         profile_name,
                         security_policy_name,
                         parameters=parameters)

def create_afd_secret(client: SecretsOperations, 
                                resource_group_name, 
                                profile_name, 
                                secret_name,                                                                
                                secret_source,
                                secret_version :str = None,
                                use_latest_version: bool = True):

    if "/certificates/" not in secret_source:
        raise CLIError('secret_source should be valid key vault certificate id.')

    if secret_version is None and not use_latest_version:
        raise CLIError('Either specify secret_version or enable use_latest_version.')

    # Only support CustomerCertificate for the moment
    parameters = CustomerCertificateParameters(
        secret_source=ResourceReference(id=secret_source),
        secret_version=secret_version,
        use_latest_version= secret_version is None
    )

    return client.create(resource_group_name,
                         profile_name,
                         secret_name,
                         parameters=parameters)

def update_afd_secret(client: SecretsOperations, 
                                resource_group_name, 
                                profile_name, 
                                secret_name,                                                                
                                secret_source : str = None,
                                secret_version :str = None,
                                use_latest_version: bool = None):

    existing = client.get(resource_group_name, profile_name, secret_name)
    
    if secret_source is not None and "/certificates/" not in secret_source:
        raise CLIError('secret_source should be valid key vault certificate id.')

    # Only support CustomerCertificate for the moment
    parameters = CustomerCertificateParameters(
        secret_source=ResourceReference(id=secret_source) if secret_source is not None else existing.paramters.secret_source,
        secret_version=secret_version,
        use_latest_version=use_latest_version
    )

    return client.create(resource_group_name,
                         profile_name,
                         secret_name,
                         parameters=parameters)

def create_afd_custom_domain(client: AFDCustomDomainsOperations,
                        resource_group_name: str,
                        profile_name: str,
                        custom_domain_name: str,
                        host_name: str,
                        certificate_type: AfdCertificateType,
                        minimum_tls_version: AfdMinimumTlsVersion, 
                        azure_dns_zone: str=None,
                        secret: str = None,
                        no_wait: bool = None):

    if azure_dns_zone is not None and "/dnszones/" not in azure_dns_zone:
        raise CLIError('azure_dns_zone should be valid azure dns zone id.')

    if secret is not None and "/secrets/" not in secret:
        raise CLIError('secret should be valid AFD secret id.')

    tls_settings = AFDDomainHttpsParameters(certificate_type=certificate_type,
                                            minimum_tls_version=minimum_tls_version,
                                            secret=ResourceReference(id=secret) if secret is not None else None)

    afd_domain = AFDDomain(host_name=host_name,
                        tls_settings=tls_settings,
                        azure_dns_zone=ResourceReference(id=azure_dns_zone) if azure_dns_zone is not None else None)

    return sdk_no_wait(no_wait, client.create, resource_group_name, profile_name, custom_domain_name, afd_domain)


def update_afd_custom_domain(client: AFDCustomDomainsOperations,
                        resource_group_name: str,
                        profile_name: str,
                        custom_domain_name: str,
                        certificate_type: AfdCertificateType = None,
                        minimum_tls_version: AfdMinimumTlsVersion = None, 
                        azure_dns_zone: str = None,
                        secret: str = None):

    if azure_dns_zone is not None and "/dnszones/" not in azure_dns_zone:
        raise CLIError('azure_dns_zone should be valid azure dns zone id.')

    if secret is not None and "/secrets/" not in secret:
        raise CLIError('secret should be valid AFD secret id.')

    existing = client.get(resource_group_name, profile_name, custom_domain_name)

    tls_settings = AFDDomainHttpsParameters(certificate_type=certificate_type,
                                            minimum_tls_version=minimum_tls_version,
                                            secret=ResourceReference(id=secret) if secret is not None else None)

    _update_mapper(existing.tls_settings, tls_settings, ["certificate_type", "minimum_tls_version", "secret"])

    afd_domain = AFDDomain(host_name=existing.host_name,
                        tls_settings=tls_settings,
                        azure_dns_zone=ResourceReference(id=azure_dns_zone) if azure_dns_zone is not None else existing.azure_dns_zone)

    return client.create(resource_group_name,
                         profile_name,
                         custom_domain_name,
                         afd_domain).result()

def _build_rule_set_put_url(subscription_id, resource_group_name, profile_name, rule_set_name, api_version):
    rule_set_url = f"/subscriptions/{subscription_id}/" \
                              f"resourceGroups/{resource_group_name}/" \
                              f"providers/Microsoft.Cdn/" \
                              f"profiles/{profile_name}/ruleSets/" \
                              f"{rule_set_name}?api-version={api_version}"
    return rule_set_url

# endregion
