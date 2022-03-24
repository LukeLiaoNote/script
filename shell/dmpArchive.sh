# ###################################################################
#                           GLOBAL VARS
# ###################################################################

#SOURCE_FILE="/home/ec2-user/option-eth/dump/matching.dmp"  # 需要备份的文件绝对路径
REMAINS=7 # 备份保留时间(day)


#__SOURCE_DIR=$(dirname ${SOURCE_FILE})
#__SOURCE_FILE_NAME=$(basename ${SOURCE_FILE})
#__BACKUP_TIME=$(date "+%Y%m%d%H%M")
#__BACKUP_FILE_NAME="${__BACKUP_TIME}-${__SOURCE_FILE_NAME}"
#__BACKUP_USER=$(id -u)





function backup(){
    if [ -f "${SOURCE_FILE}" ];
    then

        cp -f ${SOURCE_FILE} ${__SOURCE_DIR}/${__BACKUP_FILE_NAME}
        if [ $? -ne 0 ];
        then
            echo -e "\033[31m [ERROR]: backup ${SOURCE_FILE} to ${__SOURCE_DIR}/${__BACKUP_FILE_NAME} failed. Continuing...\033[0m"

        else
            echo "[SUCCESS] backup ${SOURCE_FILE} to ${__SOURCE_DIR}/${__BACKUP_FILE_NAME}"
        fi
    else
        echo -e "\033[33m[WARNING] ${SOURCE_FILE}  not exists, ignoring\033[0m"

    fi
}

function clean_legacy_backup(){
    __MATCHED_FILES=$(find ${__SOURCE_DIR}/ -type f -mtime +${REMAINS} -name "*-${__SOURCE_FILE_NAME}" -print)
    if [ ${#__MATCHED_FILES[@]} -gt 0  -a  "X${__MATCHED_FILES[0]}" != "X" ];
    then
        echo "[INFO] found legacy backups.."
        for f in ${__MATCHED_FILES};
        do
            echo "[Clean] deleting ${f} "
            rm -f ${f}
        done

    else
        echo "[INFO] No legacy backups found"

    fi
    echo "[INFO] Clean task done."
}

function eth_dump(){
    target=("/home/ec2-user/option-eth/dump/matching.dmp" "/home/ec2-user/option-eth/dump/matching_pre_stl.dmp")
    for t in ${target[@]}
    do

        SOURCE_FILE=${t}
        __SOURCE_DIR=$(dirname ${SOURCE_FILE})
        __SOURCE_FILE_NAME=$(basename ${SOURCE_FILE})
        __BACKUP_TIME=$(date "+%Y%m%d%H%M")
        __BACKUP_FILE_NAME="${__BACKUP_TIME}-${__SOURCE_FILE_NAME}"
        echo "[ETH] [INFO] Backuping ${__SOURCE_FILE_NAME} ..."

        backup
        echo "[ETH] [INFO] Cleaning legacy backups earlier than ${REMAINS} days."
        clean_legacy_backup
    done
}

function btc_dump(){
    target=("/home/ec2-user/option-btc/dump/matching.dmp" "/home/ec2-user/option-btc/dump/matching_pre_stl.dmp")
    for t in ${target[@]}
    do

        SOURCE_FILE=${t}
        __SOURCE_DIR=$(dirname ${SOURCE_FILE})
        __SOURCE_FILE_NAME=$(basename ${SOURCE_FILE})
        __BACKUP_TIME=$(date "+%Y%m%d%H%M")
        __BACKUP_FILE_NAME="${__BACKUP_TIME}-${__SOURCE_FILE_NAME}"
        echo "[BTC] [INFO] Backuping ${__SOURCE_FILE_NAME} ..."
        backup
        echo "[BTC] [INFO] Cleaning legacy backups earlier than ${REMAINS} days."
        clean_legacy_backup
    done

}

function margin_dump(){
    target=("/home/ec2-user/xderi-margin/dump/matching.dmp" "/home/ec2-user/xderi-margi/dump/matching_pre_stl.dmp")
    for t in ${target[@]}
    do

        SOURCE_FILE=${t}
        __SOURCE_DIR=$(dirname ${SOURCE_FILE})
        __SOURCE_FILE_NAME=$(basename ${SOURCE_FILE})
        __BACKUP_TIME=$(date "+%Y%m%d%H%M")
        __BACKUP_FILE_NAME="${__BACKUP_TIME}-${__SOURCE_FILE_NAME}"
        echo "[MARGIN] [INFO] Backuping ${__SOURCE_FILE_NAME} ..."
        backup
        echo "[MARGIN] [INFO] Cleaning legacy backups earlier than ${REMAINS} days."
        clean_legacy_backup
    done

}

function main(){
    case $1 in
        eth)
            eth_dump
            ;;
        btc)
            btc_dump
            ;;
        margin)
            margin_dump
            ;;
        *)
            echo "Invalid params."
            ;;
    esac
}


main $@


