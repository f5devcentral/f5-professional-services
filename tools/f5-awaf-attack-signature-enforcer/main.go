package main

import (
	"fmt"
	"os"
)

func main() {

	var err error
	var args Args

	err = GetSensitiveArgs(&args)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	err = GetArgs(&args)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	awaf := NewAWAFSystem(args.device, args.username, args.password)

	err = awaf.LoadPolicies()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	switch args.action {

	case "list-waf-policies":

		awaf.ListPolicies()

	case "list-attack-signatures":

		policy, err := awaf.GetPolicy(args.policy)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		err = policy.LoadAttackSignatures()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		err = policy.ListAttackSignatures(args.sigstatus)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

	case "print-enforcement-summary":

		if args.policy == "" {

			err = awaf.LoadAttackSignaruresAllPolicies()
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}

			err = awaf.PrintSignaturesEnforcementReadinessSummaryAllPolicies()
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}

		} else {

			policy, err := awaf.GetPolicy(args.policy)
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}

			err = policy.LoadAttackSignatures()
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}

			err = policy.PrintSignaturesEnforcementReadinessSummary()
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}

		}

	case "enforce-ready-signatures":

		policy, err := awaf.GetPolicy(args.policy)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		err = policy.LoadAttackSignatures()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		err = policy.EnforceSignaturesReadyToBeEnforced()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

	}

}
