# IPSLA

The objective of the IPSLA project is to test circuits to detect ALG routers and to to test the rtp performance of the circuit.


# HOW TO USE

The system has two modes, SERVER and CLIENT, the SERVER should be running in the first and the last rtp address of the rtp range. For ALG tests, your server needs to run OPENSIPS with a simple script for ALG detection. 

To run the SERVER use:

```bash
pysipctl SERVER rtp --host <your_host> --port <port>
```

To run the CLIENT rtp test use:

```bash
pysipctl CLIENT rtp --host <server_host> --port <server_port> --loops <number_of_loops>
```

Where:

<server_host> is the server host to be tested\
<server_port> is the server port to be tested\
<number_of_loops> is the number of loops to be tested

Use the first and the last port of your RTP range

To run an ALG test, you need to have an OpenSIPS Server set with the ALG detector installed

```bash
pysipctl CLIENT alg --host <server_host> --port <server_port> --test <test_number>
```

where <test_number> is the type of test 

1 - Test Contact if original
2 - Test Via if original
4 - Test SDP if original

The test is of match type "ANY" the default is 7 (All tests)

The responses will be ALG detected, No ALG detected



