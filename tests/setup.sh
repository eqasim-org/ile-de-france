mkdir env
cd env

# Anaconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/env/miniconda
source "$HOME/env/miniconda/etc/profile.d/conda.sh"
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda env create -f environment.yml
rm miniconda.sh

# Java
wget https://github.com/AdoptOpenJDK/openjdk8-binaries/releases/download/jdk8u252-b09/OpenJDK8U-jdk_x64_linux_hotspot_8u252b09.tar.gz -O java.tar.gz
tar xf java.tar.gz
rm java.tar.gz

# Maven
wget http://mirror.easyname.ch/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz -O maven.tar.gz
tar xf maven.tar.gz
rm maven.tar.gz

# Osmosis
wget https://github.com/openstreetmap/osmosis/releases/download/0.48.2/osmosis-0.48.2.tgz -O osmosis.tgz
mkdir $HOME/env/osmosis
tar xf osmosis.tgz -C $HOME/env/osmosis
rm osmosis.tgz

# Done
echo "done" > $HOME/env/done
