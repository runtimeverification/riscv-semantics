ARG K_VERSION
FROM runtimeverificationinc/kframework-k:ubuntu-jammy-${K_VERSION}

ARG PYTHON_VERSION=3.10

RUN    apt-get -y update             \
    && apt-get -y install            \
         graphviz                    \
         python${PYTHON_VERSION}     \
         python${PYTHON_VERSION}-dev \
         autoconf                    \
         automake                    \
         autotools-dev               \
         curl                        \
         libmpc-dev                  \
         libmpfr-dev                 \
         libgmp-dev                  \
         gawk                        \
         build-essential             \
         bison                       \
         flex                        \
         texinfo                     \
         gperf                       \
         libtool                     \
         patchutils                  \
         bc                          \
         zlib1g-dev                  \
         libexpat-dev                \
    && apt-get -y clean

ARG USER_ID=9876
ARG GROUP_ID=9876
RUN    groupadd -g ${GROUP_ID} user \
    && useradd -m -u ${USER_ID} -s /bin/bash -g user user

USER user
WORKDIR /home/user

ENV PATH=/home/user/.local/bin:${PATH}
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN pip3 install git+https://github.com/riscv/riscof.git

ENV RISCV=/opt/riscv
ENV PATH=$PATH:$RISCV/bin

RUN git clone --recursive https://github.com/riscv/riscv-gnu-toolchain -b 2024.04.12 && \
    cd riscv-gnu-toolchain && \
    ./configure --prefix=$RISCV --enable-multilib && \
    make && \
    cd .. && \
    rm -rf riscv-gnu-toolchain
