# DRG_PATH="/lus/scratch/drozt/repos/rhapdev/dragon/src"
DRG_PATH="/lus/scratch/drozt/repos/rhapdev/raddex/venv/lib/python3.12/site-packages/dragon"
SR_PATH="/lus/scratch/drozt/repos/ssimdev/sr/install/share/cmake/smartredis"

rm -rf build
mkdir build
cd build

CC=cc \
CXX=CC \
DRAGON_BASE_DIR=${DRG_PATH} \
smartredis_DIR=${SR_PATH} \
cmake \
    .. \
    -DBUILD_EXAMPLES=on

make
