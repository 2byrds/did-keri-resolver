#!/bin/bash

# To run this script you need to run the following command in a separate terminals:
#   > kli witness demo
# and from the vLEI repo run:
#   > vLEI-server -s ./schema/acdc -c ./samples/acdc/ -o ./samples/oobis/
#

# EHOuGiHMxJShXHgSb6k_9pqxmRb8H-LT0R2hQouHp8pW
echo 'creating external AID'
kli init --name external --salt 0ACDEyMzQ1Njc4OWxtbm9GhI --nopasscode --config-dir "${KERI_SCRIPT_DIR}" --config-file demo-witness-oobis-schema
kli incept --name external --alias external --file "${KERI_DEMO_SCRIPT_DIR}"/data/gleif-sample.json

# EHMnCf8_nIemuPx-cUHaDQq8zSnQIFAurdEpwHpNbnvX
echo 'creating qvi AID'
kli init --name qvi --salt 0ACDEyMzQ1Njc4OWxtbm9aBc --nopasscode --config-dir "${KERI_SCRIPT_DIR}" --config-file demo-witness-oobis-schema
kli incept --name qvi --alias qvi --file "${KERI_DEMO_SCRIPT_DIR}"/data/gleif-sample.json

# EIitNxxiNFXC1HDcPygyfyv3KUlBfS_Zf-ZYOvwjpTuz
echo 'creating legal-entity AID'
kli init --name legal-entity --salt 0ACDEyMzQ1Njc4OWxtbm9AbC --nopasscode --config-dir "${KERI_SCRIPT_DIR}" --config-file demo-witness-oobis-schema
kli incept --name legal-entity --alias legal-entity --file "${KERI_DEMO_SCRIPT_DIR}"/data/gleif-sample.json

# EBcIURLpxmVwahksgrsGW6_dUw0zBhyEHYFk17eWrZfk
# python "${KERI_SCRIPT_DIR}"/create_agent.py
# python "${KERI_SCRIPT_DIR}"/create_person_aid.py

echo 'resolving external'
kli oobi resolve --name qvi --oobi-alias external --oobi http://127.0.0.1:5642/oobi/EHOuGiHMxJShXHgSb6k_9pqxmRb8H-LT0R2hQouHp8pW/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
kli oobi resolve --name legal-entity --oobi-alias external --oobi http://127.0.0.1:5642/oobi/EHOuGiHMxJShXHgSb6k_9pqxmRb8H-LT0R2hQouHp8pW/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
echo 'resolving qvi'
kli oobi resolve --name external --oobi-alias qvi --oobi http://127.0.0.1:5642/oobi/EHMnCf8_nIemuPx-cUHaDQq8zSnQIFAurdEpwHpNbnvX/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
kli oobi resolve --name legal-entity --oobi-alias qvi --oobi http://127.0.0.1:5642/oobi/EHMnCf8_nIemuPx-cUHaDQq8zSnQIFAurdEpwHpNbnvX/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
echo 'resolving legal-entity'
kli oobi resolve --name external --oobi-alias legal-entity --oobi http://127.0.0.1:5642/oobi/EIitNxxiNFXC1HDcPygyfyv3KUlBfS_Zf-ZYOvwjpTuz/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
kli oobi resolve --name qvi --oobi-alias legal-entity --oobi http://127.0.0.1:5642/oobi/EIitNxxiNFXC1HDcPygyfyv3KUlBfS_Zf-ZYOvwjpTuz/witness/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha
# echo 'resolving person'
# kli oobi resolve --name external --oobi-alias person --oobi http://127.0.0.1:3902/oobi/EBcIURLpxmVwahksgrsGW6_dUw0zBhyEHYFk17eWrZfk/agent/EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei
# kli oobi resolve --name qvi --oobi-alias person --oobi http://127.0.0.1:3902/oobi/EBcIURLpxmVwahksgrsGW6_dUw0zBhyEHYFk17eWrZfk/agent/EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei
# kli oobi resolve --name legal-entity --oobi-alias person --oobi http://127.0.0.1:3902/oobi/EBcIURLpxmVwahksgrsGW6_dUw0zBhyEHYFk17eWrZfk/agent/EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei