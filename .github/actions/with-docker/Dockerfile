ARG K_VERSION
ARG TOOLCHAIN_VERSION

ARG TOOLCHAIN_VERSION
FROM runtimeverificationinc/riscv-gnu-toolchain:ubuntu-jammy-${TOOLCHAIN_VERSION} as TOOLCHAIN

FROM registry.gitlab.com/incoresemi/docker-images/compliance:latest as SAIL

ARG K_VERSION
FROM runtimeverificationinc/kframework-k:ubuntu-jammy-${K_VERSION}

ARG PYTHON_VERSION=3.10

RUN    apt-get -y update             \
    && apt-get -y install            \
         curl                        \
         graphviz                    \
         python${PYTHON_VERSION}     \
         python${PYTHON_VERSION}-dev \
    && apt-get -y clean

ARG USER_ID=9876
ARG GROUP_ID=9876
RUN    groupadd -g ${GROUP_ID} user \
    && useradd -m -u ${USER_ID} -s /bin/bash -g user user

USER user
WORKDIR /home/user

ENV PATH=/home/user/.local/bin:${PATH}

COPY --from=TOOLCHAIN /opt/riscv /home/user/riscv
ENV PATH=/home/user/riscv/bin:${PATH}

COPY --from=SAIL /usr/bin/riscv_sim_RV32 /usr/bin/riscv_sim_RV32
COPY --from=SAIL /usr/bin/riscv_sim_RV64 /usr/bin/riscv_sim_RV64

ARG UV_VERSION
RUN    curl -LsSf https://astral.sh/uv/$UV_VERSION/install.sh | sh \
    && uv --version
