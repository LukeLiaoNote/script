#!/bin/bash
declare -A java
java=(
        ["prod-test"]="prod-test"
)

ns=java

install_all() {
        for project in $(echo ${!java[*]}); do
                dir=${java[$project]}
                echo -e "\033[42;34m helm install $project for dir:$dir\033[0m"
                helm -n $ns install $project /home/ec2-user/prod-helm/java/$dir
        done

}

delete_all() {
        for project in $(echo ${!java[*]}); do
                dir=${java[$project]}
                echo -e "\033[42;34m helm delete $project for dir:$dir\033[0m"
                helm -n $ns delete $project
        done

}

upgrade_all() {
        for project in $(echo ${!java[*]}); do
                dir=${java[$project]}
                echo -e "\033[42;34m helm upgrade  $project for dir:$dir\033[0m"
                helm -n $ns upgrade $project /home/ec2-user/prod-helm/java/$dir
        done

}

main() {
        case $1 in
        install)
                install_all
                ;;
        delete)
                delete_all
                ;;
        upgrade)
                upgrade_all
                ;;
        esac
}

main $@