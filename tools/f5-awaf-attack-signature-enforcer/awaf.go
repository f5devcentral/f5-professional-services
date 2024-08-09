package main

import (
	"bytes"
	"crypto/tls"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"time"
)

type AWAFSystem struct {
	device   string
	username string
	password string
	policies map[string]*Policy
}

type Policy struct {
	id              string
	enforcementMode string
	awaf            *AWAFSystem
	signatures      []Signature
}

type Signature struct {
	name                                       string
	id                                         string
	alarm                                      bool
	block                                      bool
	learn                                      bool
	performStaging                             bool
	hasSuggestions                             bool
	wasUpdatedWithinEnforcementReadinessPeriod bool
	isPriorRuleEnforced                        bool
}

type EnforcementReadinessSummary struct {
	total                         int
	notEnforced                   int
	notEnforcedAndHaveSuggestions int
	readyToBeEnforced             int
	enforced                      int
	enforcedAndHaveSuggestions    int
}

func NewAWAFSystem(device, username, password string) *AWAFSystem {
	return &AWAFSystem{
		device:   device,
		username: username,
		password: password,
		policies: make(map[string]*Policy),
	}
}

func (a *AWAFSystem) LoadPolicies() error {

	basic_auth_header := "Basic " + base64.StdEncoding.EncodeToString([]byte(a.username+":"+a.password))

	url := "https://" + a.device + "/mgmt/tm/asm/policies?$select=fullPath,id,enforcementMode"

	// create a new GET request
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		errormsg := fmt.Sprintf("Error creating request: %s", err)
		return errors.New(errormsg)
	}

	// add required HTTP request headers
	req.Header.Set("Authorization", basic_auth_header)

	// create a custom HTTP Transport to skip TLS certificate verification (e.g self-signed certificates)
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	// create a custom HTTP Client using the custom HTTP Transport
	client := &http.Client{Transport: tr}

	// perform the request
	resp, err := client.Do(req)
	if err != nil {
		errormsg := fmt.Sprintf("Error making request: %s", err)
		return errors.New(errormsg)
	}
	defer resp.Body.Close()

	// fail if HTTP status code is not 200 (OK)
	if resp.StatusCode != http.StatusOK {
		errormsg := fmt.Sprintf("Request failed with %d status code", resp.StatusCode)
		return errors.New(errormsg)
	}

	// read the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		errormsg := fmt.Sprintf("Error reading response: %s", err)
		return errors.New(errormsg)
	}

	// unmarshal the JSON response into a map
	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	if err != nil {
		errormsg := fmt.Sprintf("Error unmarshalling JSON: %s", err)
		return errors.New(errormsg)
	}

	if policies, ok := response["items"].([]interface{}); ok {
		for _, policyItem := range policies {
			if policy, ok := policyItem.(map[string]interface{}); ok {
				fullPath := policy["fullPath"].(string)
				id := policy["id"].(string)
				enforcementMode := policy["enforcementMode"].(string)
				a.policies[fullPath] = &Policy{id: id, enforcementMode: enforcementMode, awaf: a}
			}
		}
	}

	return nil
}

func (a *AWAFSystem) ListPolicies() {

	if a.policies == nil || len(a.policies) == 0 {
		fmt.Println("No policies found.")
		return
	}

	fmt.Printf("%-30s %-25s %-20s\n", "policy", "id", "enforcementMode")

	for key, policy := range a.policies {
		name := key
		id := policy.id
		enforcementMode := policy.enforcementMode
		fmt.Printf("%-30s %-25s %-20s\n", name, id, enforcementMode)
	}
}

func (a AWAFSystem) PolicyExists(policyName string) bool {

	_, exists := a.policies[policyName]
	if !exists {
		return false
	}

	return true
}

func (a *AWAFSystem) GetPolicy(policyName string) (*Policy, error) {

	if a.PolicyExists(policyName) == false {
		errormsg := "Policy not found."
		return &Policy{}, errors.New(errormsg)
	}

	policy := a.policies[policyName]

	return policy, nil
}

func (p *Policy) LoadAttackSignatures() error {

	p.signatures = p.signatures[:0]

	basic_auth_header := "Basic " + base64.StdEncoding.EncodeToString([]byte(p.awaf.username+":"+p.awaf.password))

	asmSelect := "signatureReference,alarm,block,learn,performStaging,hasSuggestions,wasUpdatedWithinEnforcementReadinessPeriod,isPriorRuleEnforced"

	url := "https://" + p.awaf.device + "/mgmt/tm/asm/policies/" + p.id + "/signatures?$select=" + asmSelect

	// create an HTTP GET request
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		errormsg := fmt.Sprintf("Error creating request: %s", err)
		return errors.New(errormsg)
	}

	// add required HTTP request headers
	req.Header.Set("Authorization", basic_auth_header)

	// create a custom HTTP Transport to skip TLS certificate verification (e.g self-signed certificates)
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	// create a custom HTTP Client using the custom HTTP Transport
	client := &http.Client{Transport: tr}

	// perform the request
	resp, err := client.Do(req)
	if err != nil {
		errormsg := fmt.Sprintf("Error making request: %s", err)
		return errors.New(errormsg)
	}
	defer resp.Body.Close()

	// fail if HTTP status code is not 200 (OK)
	if resp.StatusCode != http.StatusOK {
		errormsg := fmt.Sprintf("Request failed with %d status code", resp.StatusCode)
		return errors.New(errormsg)
	}

	// read the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		errormsg := fmt.Sprintf("Error reading response: %s", err)
		return errors.New(errormsg)
	}

	// unmarshal the JSON response into a map
	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	if err != nil {
		errormsg := fmt.Sprintf("Error unmarshalling JSON: %s", err)
		return errors.New(errormsg)
	}

	if signatures, ok := response["items"].([]interface{}); ok {
		for _, signatureItem := range signatures {
			if signature, ok := signatureItem.(map[string]interface{}); ok {
				var name string
				var id string
				var alarm, block, learn, performStaging, hasSuggestions, wasUpdatedWithinEnforcementReadinessPeriod, isPriorRuleEnforced bool
				if signatureReference, ok := signature["signatureReference"].(map[string]interface{}); ok {
					name = signatureReference["name"].(string)
					id = fmt.Sprintf("%.0f", signatureReference["signatureId"].(float64))
				}
				alarm = signature["alarm"].(bool)
				block = signature["block"].(bool)
				learn = signature["learn"].(bool)
				performStaging = signature["performStaging"].(bool)
				hasSuggestions = signature["hasSuggestions"].(bool)
				wasUpdatedWithinEnforcementReadinessPeriod = signature["wasUpdatedWithinEnforcementReadinessPeriod"].(bool)
				isPriorRuleEnforced = signature["isPriorRuleEnforced"].(bool)
				p.signatures = append(p.signatures, Signature{
					name:           name,
					id:             id,
					alarm:          alarm,
					block:          block,
					learn:          learn,
					performStaging: performStaging,
					hasSuggestions: hasSuggestions,
					wasUpdatedWithinEnforcementReadinessPeriod: wasUpdatedWithinEnforcementReadinessPeriod,
					isPriorRuleEnforced:                        isPriorRuleEnforced,
				})
			}
		}
	}

	return nil
}

func (a *AWAFSystem) LoadAttackSignaruresAllPolicies() error {

	for _, policy := range a.policies {
		err := policy.LoadAttackSignatures()
		if err != nil {
			return (err)
		}
	}

	return nil
}

func (p *Policy) ListAttackSignatures(sigstatus string) error {

	if p.signatures == nil {
		errormsg := fmt.Sprintf("Attack signatures not found/loaded.")
		return errors.New(errormsg)
	}

	if sigstatusIsAllowed(sigstatus) == false {
		errorsmg := fmt.Sprintf("Invalid signature status. Allowed values are: 'all','ready to be enforced','not enforced (has suggestions)','not enforced','enforced (has suggestions)','enforced'.")
		return errors.New(errorsmg)
	}

	fmt.Printf("%-50s %-20s %-15s %-15s %-15s %-25s\n", "name", "id", "learn", "alarm", "block", "status")

	for _, signature := range p.signatures {

		name := signature.name
		id := signature.id
		learn := signature.learn
		alarm := signature.alarm
		block := signature.block
		performStaging := signature.performStaging
		hasSuggestions := signature.hasSuggestions
		wasUpdatedWithinEnforcementReadinessPeriod := signature.wasUpdatedWithinEnforcementReadinessPeriod

		var status string

		if performStaging {

			if (!wasUpdatedWithinEnforcementReadinessPeriod) && (!hasSuggestions) {
				status = "ready to be enforced"
			} else {
				if hasSuggestions {
					status = "not enforced (has suggestions)"
				} else {
					status = "not enforced"
				}
			}

		} else {

			if hasSuggestions {
				status = "enforced (has suggestions)"
			} else {
				status = "enforced"
			}

		}

		if (sigstatus == "all") || (sigstatus == status) {
			fmt.Printf("%-50s %-20s %-15t %-15t %-15t %-25s\n", name, id, learn, alarm, block, status)
		}
	}

	return nil
}

func (p Policy) GetSignatureEnforcementReadinessSummary() (EnforcementReadinessSummary, error) {

	if p.signatures == nil {
		errormsg := fmt.Sprintf("Attack signatures not found/loaded.")
		return EnforcementReadinessSummary{}, errors.New(errormsg)
	}

	total := len(p.signatures)
	notEnforced := 0
	notEnforcedAndHaveSuggestions := 0
	readyToBeEnforced := 0
	enforced := 0
	enforcedAndHaveSuggestions := 0

	for _, signature := range p.signatures {

		if signature.performStaging {
			notEnforced += 1
			if signature.hasSuggestions {
				notEnforcedAndHaveSuggestions += 1
			} else {
				if !signature.wasUpdatedWithinEnforcementReadinessPeriod {
					readyToBeEnforced += 1
				}
			}
		} else {
			enforced += 1
			if signature.hasSuggestions {
				enforcedAndHaveSuggestions += 1
			}
		}

	}

	summary := EnforcementReadinessSummary{
		total:                         total,
		notEnforced:                   notEnforced,
		notEnforcedAndHaveSuggestions: notEnforcedAndHaveSuggestions,
		readyToBeEnforced:             readyToBeEnforced,
		enforced:                      enforced,
		enforcedAndHaveSuggestions:    enforcedAndHaveSuggestions,
	}

	return summary, nil
}

func (p Policy) PrintSignaturesEnforcementReadinessSummary() error {

	summary, err := p.GetSignatureEnforcementReadinessSummary()
	if err != nil {
		return err
	}

	fmt.Printf("%-8s | %-12s | %-32s | %-20s | %-8s | %-30s\n", "Total", "Not Enforced", "Not Enforced (Have Suggestions)", "Ready To Be Enforced", "Enforced", "Enforced (Have Suggestions)")
	fmt.Printf("%-8d | %-12d | %-32d | %-20d | %-8d | %-30d\n",
		summary.total,
		summary.notEnforced,
		summary.notEnforcedAndHaveSuggestions,
		summary.readyToBeEnforced,
		summary.enforced,
		summary.enforcedAndHaveSuggestions)

	return nil
}

func (a AWAFSystem) PrintSignaturesEnforcementReadinessSummaryAllPolicies() error {

	fmt.Printf("%-30s | %-8s | %-12s | %-32s | %-20s | %-8s | %-30s\n", "Policy", "Total", "Not Enforced", "Not Enforced (Have Suggestions)", "Ready To Be Enforced", "Enforced", "Enforced (Have Suggestions)")

	for policyName := range a.policies {

		policy := a.policies[policyName]

		summary, err := policy.GetSignatureEnforcementReadinessSummary()
		if err != nil {
			return err
		}

		fmt.Printf("%-30s | %-8d | %-12d | %-32d | %-20d | %-8d | %-30d\n", policyName,
			summary.total,
			summary.notEnforced,
			summary.notEnforcedAndHaveSuggestions,
			summary.readyToBeEnforced,
			summary.enforced,
			summary.enforcedAndHaveSuggestions)

	}

	return nil
}

func (p Policy) EnforceSignaturesReadyToBeEnforced() error {

	if p.signatures == nil {
		errormsg := fmt.Sprintf("Attack signatures not found/loaded.")
		return errors.New(errormsg)
	}

	summary, err := p.GetSignatureEnforcementReadinessSummary()
	if err != nil {
		return err
	}

	if summary.readyToBeEnforced == 0 {
		fmt.Println("No attack signatures ready to be enforced were found.")
		return nil
	}

	basic_auth_header := "Basic " + base64.StdEncoding.EncodeToString([]byte(p.awaf.username+":"+p.awaf.password))

	asmFilter := "hasSuggestions+eq+false+AND+wasUpdatedWithinEnforcementReadinessPeriod+eq+false+and+performStaging+eq+true"

	url := "https://" + p.awaf.device + "/mgmt/tm/asm/policies/" + p.id + "/signatures?$select=&$filter=" + asmFilter

	data := map[string]any{
		"performStaging": false,
	}

	jsonData, err := json.Marshal(data)
	if err != nil {
		errormsg := fmt.Sprintf("Error encoding JSON: %s", err)
		return errors.New(errormsg)
	}

	// create an HTTP PATCH request
	req, err := http.NewRequest("PATCH", url, bytes.NewBuffer(jsonData))
	if err != nil {
		errormsg := fmt.Sprintf("Error creating request: %s", err)
		return errors.New(errormsg)
	}

	// add required HTTP request headers
	req.Header.Set("Authorization", basic_auth_header)
	req.Header.Set("Content-Type", "application/json")

	// create a custom HTTP Transport to skip TLS certificate verification (e.g self-signed certificates)
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	// create a custom HTTP Client using the custom HTTP Transport
	client := &http.Client{Transport: tr}

	// perform the request
	resp, err := client.Do(req)
	if err != nil {
		errormsg := fmt.Sprintf("Error making request: %s", err)
		return errors.New(errormsg)
	}
	defer resp.Body.Close()

	// fail if HTTP status code is not 200
	if resp.StatusCode != http.StatusOK {
		errormsg := fmt.Sprintf("Request failed with %d status code", resp.StatusCode)
		return errors.New(errormsg)
	}

	// read the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		errormsg := fmt.Sprintf("Error reading response: %s", err)
		return errors.New(errormsg)
	}

	// unmarshal the JSON response into a map
	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	if err != nil {
		errormsg := fmt.Sprintf("Error unmarshalling JSON: %s", err)
		return errors.New(errormsg)
	}

	totalItems := result["totalItems"].(float64)
	fmt.Printf("%d signatures enforced.\n", int(totalItems))

	err = p.ApplyPolicy()
	if err != nil {
		return err
	}

	return nil
}

func (p Policy) ApplyPolicy() error {

	basic_auth_header := "Basic " + base64.StdEncoding.EncodeToString([]byte(p.awaf.username+":"+p.awaf.password))

	url := "https://" + p.awaf.device + "/mgmt/tm/asm/tasks/apply-policy"

	data := map[string]interface{}{
		"policyReference": map[string]string{
			"link": "https://" + p.awaf.device + "/mgmt/tm/asm/policies/" + p.id,
		},
	}

	jsonData, err := json.Marshal(data)
	if err != nil {
		errormsg := fmt.Sprintf("Error encoding JSON: %s", err)
		return errors.New(errormsg)
	}

	// create an HTTP POST request
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		errormsg := fmt.Sprintf("Error creating request: %s", err)
		return errors.New(errormsg)
	}

	// add required HTTP request headers
	req.Header.Set("Authorization", basic_auth_header)
	req.Header.Set("Content-Type", "application/json")

	// create a custom HTTP Transport to skip TLS certificate verification (e.g self-signed certificates)
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	// create a custom HTTP Client using the custom HTTP Transport
	client := &http.Client{Transport: tr}

	// running a 'apply-policy' operation to apply the policy changes
	fmt.Printf("Running an 'apply-policy' operation on the policy.\n")

	// perform the request
	resp, err := client.Do(req)
	if err != nil {
		errormsg := fmt.Sprintf("Error making request: %s", err)
		return errors.New(errormsg)
	}
	defer resp.Body.Close()

	// fail if HTTP status code is not 201 (Created)
	if resp.StatusCode != http.StatusCreated {
		errormsg := fmt.Sprintf("Request failed with %d status code", resp.StatusCode)
		return errors.New(errormsg)
	}

	// read the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		errormsg := fmt.Sprintf("Error reading response: %s", err)
		return errors.New(errormsg)
	}

	// unmarshal the JSON response into a map
	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	if err != nil {
		errormsg := fmt.Sprintf("Error unmarshalling JSON: %s", err)
		return errors.New(errormsg)
	}

	status := response["status"].(string)
	task_id := response["id"].(string)

	if status != "NEW" {
		errormsg := fmt.Sprintf("Apply policy task failed.")
		return errors.New(errormsg)
	}

	url = "https://" + p.awaf.device + "/mgmt/tm/asm/tasks/apply-policy/" + task_id

	interval := 1 * time.Second
	timeout := 5 * time.Minute
	startTime := time.Now()

	var finalStatus string

	// waiting for the 'apply-policy' operation to complete (or fail or time out)

	for time.Since(startTime) < timeout {

		// create an HTTP GET request
		req, err := http.NewRequest("GET", url, nil)
		if err != nil {
			errormsg := fmt.Sprintf("Error creating request: %s", err)
			return errors.New(errormsg)
		}

		// add required HTTP resquest headers
		req.Header.Set("Authorization", basic_auth_header)

		// create a custom HTTP Client using the custom HTTP Transport
		client := &http.Client{Transport: tr}

		// perform the request
		resp, err := client.Do(req)
		if err != nil {
			errormsg := fmt.Sprintf("Error making request: %s", err)
			return errors.New(errormsg)
		}

		// fail if HTTP status code is not 200 (OK)
		if resp.StatusCode != http.StatusOK {
			errormsg := fmt.Sprintf("Request failed with %d status code", resp.StatusCode)
			return errors.New(errormsg)
		}

		// read the response body
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			errormsg := fmt.Sprintf("Error reading response body: %s", err)
			resp.Body.Close()
			return errors.New(errormsg)
		}

		resp.Body.Close()

		// unmarshal the JSON response into a map
		var response map[string]interface{}
		if err := json.Unmarshal(body, &response); err != nil {
			errormsg := fmt.Sprintf("Error parsing JSON: %s", err)
			return errors.New(errormsg)
		}

		if status, exists := response["status"]; exists && status == "COMPLETED" {
			finalStatus = status.(string)
			break
		}

		time.Sleep(interval)

	}

	if finalStatus != "COMPLETED" {
		errormsg := fmt.Sprintf("Apply policy task failed or timed out.")
		return errors.New(errormsg)
	}

	fmt.Println("The 'apply-policy' task completed successfully.")

	return nil
}

func sigstatusIsAllowed(sigstatus string) bool {

	allowedStatuses := []string{
		"all",
		"ready to be enforced",
		"not enforced (has suggestions)",
		"not enforced",
		"enforced (has suggestions)",
		"enforced",
	}

	for _, status := range allowedStatuses {
		if status == sigstatus {
			return true
		}
	}

	return false
}
