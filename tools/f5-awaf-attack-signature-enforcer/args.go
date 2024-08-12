package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
)

type Args struct {
	device    string
	username  string
	password  string
	action    string
	policy    string
	sigstatus string
}

func GetSensitiveArgs(args *Args) error {

	device, exists := os.LookupEnv("BIGIP_ADDRESS")
	if !exists {
		errormsg := fmt.Sprintf("Environment variable BIGIP_ADDRESS not set.")
		return errors.New(errormsg)
	}
	args.device = device

	username, exists := os.LookupEnv("BIGIP_USERNAME")
	if !exists {
		errormsg := fmt.Sprintf("Environment variable BIGIP_USERNAME not set.")
		return errors.New(errormsg)
	}
	args.username = username

	password, exists := os.LookupEnv("BIGIP_PASSWORD")
	if !exists {
		errormsg := fmt.Sprintf("Environment variable BIGIP_PASSWORD not set.")
		return errors.New(errormsg)
	}
	args.password = password

	return nil
}

func GetArgs(args *Args) error {

	flag.StringVar(&args.action, "action", "list-waf-policies", "Specify the action. Allowed values are: 'list-waf-policies','list-attack-signatures','print-enforcement-summary','enforce-ready-signatures'.")
	flag.StringVar(&args.policy, "policy", "", "Specify the WAF policy in which the action will be performed.")
	flag.StringVar(&args.sigstatus, "sigstatus", "all", "Specify the action. Allowed values are: 'all','ready to be enforced','not enforced (has suggestions)','not enforced','enforced (has suggestions)','enforced'.")

	flag.Parse()

	if actionArgValueIsAllowed(args.action) == false {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		flag.PrintDefaults()
		return errors.New("Invalid '-action' value.")
	}

	if sigstatusArgValueIsAllowed(args.sigstatus) == false {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		flag.PrintDefaults()
		return errors.New("Invalid '-sigstatus' value.")
	}

	if ((args.action == "list-attack-signatures") || (args.action == "enforce-ready-signatures")) && (args.policy == "") {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		flag.PrintDefaults()
		return errors.New("Missing argument '-policy' (required with the specified action). ")
	}

	return nil
}

func actionArgValueIsAllowed(action string) bool {

	allowedValues := []string{
		"list-waf-policies",
		"list-attack-signatures",
		"print-enforcement-summary",
		"enforce-ready-signatures",
	}

	for _, value := range allowedValues {
		if value == action {
			return true
		}
	}

	return false
}

func sigstatusArgValueIsAllowed(sigstatus string) bool {

	allowedValues := []string{
		"all",
		"ready to be enforced",
		"not enforced (has suggestions)",
		"not enforced",
		"enforced (has suggestions)",
		"enforced",
	}

	for _, value := range allowedValues {
		if value == sigstatus {
			return true
		}
	}

	return false
}
